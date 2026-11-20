"""Exercise the generated plugin, not a reimplementation of its handoff."""
import base64
from contextlib import redirect_stdout
import importlib.util
import io
from pathlib import Path
import struct
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("builder", ROOT / "build_orca_plugin.py")
assert spec is not None and spec.loader is not None
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class LinuxImportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "export.stl").write_bytes(b"archive")
        orca = types.SimpleNamespace(
            script=types.SimpleNamespace(ScriptPluginCapabilityBase=type("Script", (), {})),
            base=type("Plugin", (), {}), plugin=lambda cls: cls)
        self.plugin = types.ModuleType("generated_gridfinity")
        with patch.object(builder, "HERE", str(self.root)), redirect_stdout(io.StringIO()):
            generated = builder.build_for_targets(
                ["linux_x86_64"], (ROOT / "gridfinity_bin.html").read_text(encoding="utf-8"))[0]
        self.plugin.__file__ = generated
        with patch.dict(sys.modules, orca=orca):
            exec(compile(Path(generated).read_text(encoding="utf-8"), generated, "exec"), self.plugin.__dict__)
        self.plugin.IS_WINDOWS = self.plugin.IS_MACOS = False
        self.plugin._log = lambda *args: None
        self.core = self.plugin._GridfinityCore()

    def test_permission_pending_stops_discovery_without_fallback_or_retry(self):
        calls = []
        def denied(argv, **kwargs):
            calls.append(argv)
            raise PermissionError('Plugin attempted audited operation "subprocess.Popen" without permission')
        with patch.object(self.plugin.subprocess, "run", side_effect=denied), \
             patch.object(self.plugin.shutil, "which", return_value="/usr/bin/bambu-studio"), \
             patch.object(self.plugin.time, "sleep"):
            problem = self.plugin.load_onto_plate(str(self.root / "export.stl"))
        self.assertIn("permission", problem.lower())
        self.assertIn("retry", problem.lower())
        self.assertEqual(len(calls), 1, calls)

    def test_permission_failure_at_each_subprocess_stops_immediately(self):
        bus = "com.orcaslicer.OrcaSlicer.InstanceCheck.Object123"
        for blocked in range(3):
            with self.subTest(blocked=blocked):
                calls = []
                def run(argv, **kwargs):
                    calls.append(argv)
                    if len(calls) == blocked + 1:
                        raise PermissionError("approval pending")
                    output = 'string "' + bus + '"' if len(calls) == 1 else 'uint32 1'
                    return types.SimpleNamespace(returncode=0, stdout=output, stderr="")
                with patch.object(self.plugin.subprocess, "run", side_effect=run), \
                     patch.object(self.plugin.time, "sleep"):
                    problem = self.plugin.load_onto_plate(str(self.root / "export.stl"))
                self.assertIsNotNone(problem)
                self.assertIn("permission", problem.lower())
                self.assertEqual(len(calls), blocked + 1)

    def test_cli_permission_failure_does_not_try_second_executable(self):
        calls = []
        def run(argv, **kwargs):
            calls.append(argv)
            if "ListNames" in argv[-1]:
                return types.SimpleNamespace(stdout="", returncode=0, stderr="")
            raise PermissionError("approval pending")
        with patch.object(self.plugin.subprocess, "run", side_effect=run), \
             patch.object(self.plugin.os.path, "realpath", return_value="/usr/bin/python"), \
             patch.object(self.plugin.shutil, "which", side_effect=lambda name: "/usr/bin/" + name), \
             patch.dict(self.plugin.os.environ, {}, clear=True), \
             patch.object(self.plugin.time, "sleep"):
            problem = self.plugin.load_onto_plate(str(self.root / "export.stl"))
        self.assertIn("permission", problem.lower())
        self.assertEqual(len(calls), 2, calls)

    def test_cli_timeout_does_not_try_second_executable(self):
        calls = []
        def run(argv, **kwargs):
            calls.append(argv)
            if len(calls) == 1:
                raise self.plugin.subprocess.TimeoutExpired(argv, 10)
            return types.SimpleNamespace(returncode=0, stdout="", stderr="")
        with patch.object(self.plugin.subprocess, "run", side_effect=run), \
             patch.object(self.plugin.os.path, "realpath", return_value="/usr/bin/python"), \
             patch.object(self.plugin.sys, "executable", "/usr/bin/python"), \
             patch.object(self.plugin.shutil, "which", side_effect=lambda name: "/usr/bin/" + name), \
             patch.dict(self.plugin.os.environ, {}, clear=True):
            problem = self.plugin._place_cli_fallback(str(self.root / "export.stl"))
        self.assertEqual(len(calls), 1, calls)
        self.assertIsNotNone(problem)
        self.assertIn("unconfirmed", problem.lower())

    def test_linux_never_discovers_bambu(self):
        with patch.object(self.plugin.os.path, "realpath", return_value="/usr/bin/python"), \
             patch.object(self.plugin.shutil, "which", return_value=None) as which, \
             patch.dict(self.plugin.os.environ, {}, clear=True):
            self.assertIsNotNone(self.plugin._place_cli_fallback("file.stl"))
        self.assertNotIn("bambu-studio", [call.args[0] for call in which.call_args_list])

    def export(self, name, data, chunked=False):
        replies = []
        payload = base64.b64encode(data).decode()
        if chunked:
            self.core._handle(dict(type="save_stl_start", name=name, total_bytes=len(data), place=True), replies.append)
            self.core._handle(dict(type="save_stl_chunk", index=0, chunk=payload), replies.append)
            self.core._handle(dict(type="save_stl_finish"), replies.append)
        else:
            self.core._handle(dict(type="save_stl", name=name, data=payload, place=True), replies.append)
        return replies

    def test_distinct_exports_reuse_command_but_preserve_archives_in_audited_callback(self):
        bus = "com.orcaslicer.OrcaSlicer.InstanceCheck.Object123"
        commands, imported = [], []
        def run(argv, **kwargs):
            commands.append(repr(argv))
            if argv[-1].endswith("ListNames"):
                output = 'string "' + bus + '"'
            elif "GetConnectionUnixProcessID" in argv[-2]:
                output = "uint32 " + str(self.plugin.os.getpid())
            else:
                target = Path(argv[-1].removeprefix("string:orca-slicer;"))
                imported.append(target.read_bytes())
                output = ""
            return types.SimpleNamespace(returncode=0, stdout=output, stderr="")
        contents = [bytes([n]) * 80 + struct.pack("<I", 1) + bytes([n]) * 50 for n in (1, 2)]
        with patch.object(self.plugin.subprocess, "run", side_effect=run), \
             patch.object(self.plugin.threading, "Thread", side_effect=AssertionError("Linux must retain host audit context")), \
             patch.object(self.plugin.time, "sleep"):
            for i, data in enumerate(contents):
                replies = self.export(f"different-{i}-timestamp.stl", data, chunked=bool(i))
                self.assertTrue(replies[-1]["placed"], replies)
                self.assertEqual(Path(replies[-1]["path"]).read_bytes(), data)
        self.assertEqual(imported, contents)
        self.assertEqual(commands[:3], commands[3:])
        self.assertEqual(len(list((self.root / "gridfinity_output").glob("*.stl"))), 2)

    def test_no_reply_is_uncertain_not_placed_and_never_retried(self):
        calls = []
        bus = "com.orcaslicer.OrcaSlicer.InstanceCheck.Object123"
        def run(argv, **kwargs):
            calls.append(argv)
            if argv[-1].endswith("ListNames"):
                return types.SimpleNamespace(returncode=0, stdout='string "' + bus + '"', stderr="")
            if "GetConnectionUnixProcessID" in argv[-2]:
                return types.SimpleNamespace(returncode=0, stdout="uint32 1", stderr="")
            return types.SimpleNamespace(returncode=1, stdout="", stderr="org.freedesktop.DBus.Error.NoReply")
        data = b"x" * 80 + struct.pack("<I", 1) + bytes(50)
        with patch.object(self.plugin.subprocess, "run", side_effect=run):
            replies = self.export("uncertain.stl", data)
        self.assertFalse(replies[-1]["placed"], replies)
        self.assertIn("confirm", replies[-1]["place_error"].lower())
        self.assertEqual(len(calls), 3, calls)

    def test_timeout_after_send_is_not_retried(self):
        bus = "com.orcaslicer.OrcaSlicer.InstanceCheck.Object123"
        calls = []
        def run(argv, **kwargs):
            calls.append(argv)
            if len(calls) == 1:
                return types.SimpleNamespace(returncode=0, stdout='string "' + bus + '"', stderr="")
            if len(calls) == 2:
                return types.SimpleNamespace(returncode=0, stdout="uint32 1", stderr="")
            raise self.plugin.subprocess.TimeoutExpired(argv, 5)
        with patch.object(self.plugin.subprocess, "run", side_effect=run):
            problem = self.plugin.load_onto_plate(str(self.root / "export.stl"))
        self.assertIsNotNone(problem)
        self.assertEqual(len(calls), 3, calls)

    def test_deferred_approvals_require_explicit_retry_and_then_reuse_exact_grants(self):
        grants, pending, calls = set(), [], []
        bus = "com.orcaslicer.OrcaSlicer.InstanceCheck.Object123"
        def audited_run(argv, **kwargs):
            target = repr(argv)
            calls.append(target)
            if target not in grants:
                pending.append(target)
                raise PermissionError("approval pending")
            output = ('string "' + bus + '"' if argv[-1].endswith("ListNames")
                      else "uint32 " + str(self.plugin.os.getpid()))
            return types.SimpleNamespace(returncode=0, stdout=output, stderr="")
        data = b"x" * 80 + struct.pack("<I", 1) + bytes(50)
        with patch.object(self.plugin.subprocess, "run", side_effect=audited_run):
            for n in range(3):
                replies = self.export(f"pending-{n}.stl", data, chunked=bool(n % 2))
                self.assertFalse(replies[-1]["placed"])
                self.assertIn("retry", replies[-1]["place_error"].lower())
                self.assertEqual(len(pending), n + 1)
                before_approval = len(calls)
                grants.add(pending[-1])
                self.assertEqual(len(calls), before_approval, "approval must not replay a queued job")
            for n in range(2):
                replies = self.export(f"approved-{n}.stl", data, chunked=bool(n))
                self.assertTrue(replies[-1]["placed"], replies)
        self.assertEqual(len(pending), 3, "new timestamp filenames must not require new grants")
        self.assertEqual(len(list((self.root / "gridfinity_output").glob("*.stl"))), 5)

    def test_reentrant_export_cannot_replace_inflight_staging(self):
        bus = "com.orcaslicer.OrcaSlicer.InstanceCheck.Object123"
        first = b"a" * 80 + struct.pack("<I", 1) + bytes(50)
        second = b"b" * 80 + struct.pack("<I", 1) + bytes(50)
        nested = []
        def run(argv, **kwargs):
            if argv[-1].endswith("ListNames"):
                output = 'string "' + bus + '"'
            elif "GetConnectionUnixProcessID" in argv[-2]:
                output = "uint32 1"
            else:
                stage = Path(argv[-1].removeprefix("string:orca-slicer;"))
                self.assertEqual(stage.read_bytes(), first)
                nested.extend(self.export("second.stl", second, chunked=True))
                self.assertEqual(stage.read_bytes(), first)
                output = ""
            return types.SimpleNamespace(returncode=0, stdout=output, stderr="")
        with patch.object(self.plugin.subprocess, "run", side_effect=run):
            replies = self.export("first.stl", first)
        self.assertTrue(replies[-1]["placed"])
        self.assertFalse(nested[-1]["placed"])
        self.assertIn("in progress", nested[-1]["place_error"])
        self.assertEqual(Path(nested[-1]["path"]).read_bytes(), second)

    def test_staging_failure_never_dispatches_or_reports_success(self):
        data = b"x" * 80 + struct.pack("<I", 1) + bytes(50)
        with patch.object(self.plugin.shutil, "copyfileobj", side_effect=OSError("disk full")), \
             patch.object(self.plugin.subprocess, "run") as run:
            replies = self.export("failed.stl", data)
        self.assertFalse(replies[-1]["placed"])
        self.assertIn("disk full", replies[-1]["place_error"])
        self.assertEqual(Path(replies[-1]["path"]).read_bytes(), data)
        run.assert_not_called()
        self.assertTrue(self.plugin._LINUX_IMPORT_LOCK.acquire(blocking=False))
        self.plugin._LINUX_IMPORT_LOCK.release()

    def test_linux_ignores_other_slicers_on_dbus(self):
        names = ('string "com.bambulab.BambuStudio.InstanceCheck.Object999"\n'
                 'string "com.orcaslicer.OrcaSlicer.InstanceCheck.Object123"')
        calls = []
        def run(argv, **kwargs):
            calls.append(argv)
            return types.SimpleNamespace(stdout=names if len(calls) == 1 else "uint32 1")
        with patch.object(self.plugin.subprocess, "run", side_effect=run):
            found = self.plugin._session_bus_names()
        self.assertEqual(found, ["com.orcaslicer.OrcaSlicer.InstanceCheck.Object123"])
        self.assertEqual(len(calls), 2)

    def test_cli_handoff_reuses_staging_path_for_distinct_exports(self):
        calls, imported = [], []
        def run(argv, **kwargs):
            calls.append(repr(argv))
            if not argv[-1].endswith("ListNames"):
                imported.append(Path(argv[-1]).read_bytes())
            return types.SimpleNamespace(returncode=0, stdout="", stderr="")
        contents = [bytes([n]) * 80 + struct.pack("<I", 1) + bytes(50) for n in (1, 2)]
        with patch.object(self.plugin.subprocess, "run", side_effect=run), \
             patch.object(self.plugin.os.path, "realpath", return_value="/usr/bin/python"), \
             patch.object(self.plugin.sys, "executable", "/usr/bin/python"), \
             patch.object(self.plugin.shutil, "which", side_effect=lambda n: "/usr/bin/orca-slicer" if n == "orca-slicer" else None), \
             patch.dict(self.plugin.os.environ, {}, clear=True):
            for n, data in enumerate(contents):
                replies = self.export(f"cli-{n}.stl", data, chunked=bool(n))
                self.assertTrue(replies[-1]["placed"], replies)
        self.assertEqual(calls[:2], calls[2:])
        self.assertEqual(imported, contents)


class GeneratedArtifactsTests(unittest.TestCase):
    def test_all_six_tracked_plugins_match_deterministic_builder_output(self):
        html = (ROOT / "gridfinity_bin.html").read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as tmp, \
             patch.object(builder, "HERE", tmp), redirect_stdout(io.StringIO()):
            paths = builder.build_for_targets(builder.SUPPORTED_TARGETS, html)
            first = {Path(path).name: Path(path).read_bytes() for path in paths}
            builder.build_for_targets(builder.SUPPORTED_TARGETS, html)
            self.assertEqual(len(first), 6)
            for path in paths:
                name = Path(path).name
                self.assertEqual(Path(path).read_bytes(), first[name], name)
                self.assertEqual((ROOT / name).read_bytes(), first[name], name)


if __name__ == "__main__":
    unittest.main()

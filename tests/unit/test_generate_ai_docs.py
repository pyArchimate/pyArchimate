"""Unit tests for scripts/generate_ai_docs.py (T003, T004, T010, T015)."""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import generate_ai_docs as gen


class TestValidateMarkdownStructure:
    def test_all_sections_present(self):
        content = "\n".join(f"# {s}" for s in gen.REQUIRED_SECTIONS)
        assert gen.validate_markdown_structure(content) == []

    def test_returns_missing_sections(self):
        content = "# Summary\n\n# Overview\n"
        missing = gen.validate_markdown_structure(content)
        assert "Core Purpose" in missing
        assert "Summary" not in missing

    def test_fuzzy_match_on_verbose_headings(self):
        content = (
            "# Summary\n# Overview\n# Core Purpose\n"
            "# Conceptual Model (Metamodel Support)\n"
            "# Key Features & Functionality\n"
            "# Typical Use Cases\n# Strengths\n"
            "# Limitations (Important Context)\n# Non-Conformances\n"
        )
        assert gen.validate_markdown_structure(content) == []

    def test_empty_content_returns_all_missing(self):
        assert len(gen.validate_markdown_structure("")) == len(gen.REQUIRED_SECTIONS)


class TestValidateMarkdownSyntax:
    @patch("generate_ai_docs.subprocess.run")
    def test_returns_true_on_clean_scan(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        assert gen.validate_markdown_syntax("# Summary\n\nText.\n") is True

    @patch("generate_ai_docs.subprocess.run")
    def test_returns_false_on_lint_errors(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="lint error")
        assert gen.validate_markdown_syntax("bad\tcontent") is False


class TestGetApiKey:
    def test_returns_key_when_set(self) -> None:
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test-123"}):
            assert gen.get_api_key() == "sk-test-123"

    def test_returns_empty_string_when_not_set(self) -> None:
        env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
        with patch.dict(os.environ, env, clear=True):
            assert gen.get_api_key() == ""


class TestRunClaude:
    @patch("generate_ai_docs.subprocess.run")
    def test_returns_stdout_on_success(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(returncode=0, stdout="# Summary\n", stderr="")
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "key"}):
            assert gen.run_claude("prompt") == "# Summary\n"

    @patch("generate_ai_docs.subprocess.run")
    def test_raises_on_nonzero_exit(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="fail")
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "key"}):
            with pytest.raises(RuntimeError, match="claude exited"):
                gen.run_claude("prompt")

    @patch("generate_ai_docs.subprocess.run")
    def test_raises_on_empty_output(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(returncode=0, stdout="  ", stderr="")
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "key"}):
            with pytest.raises(RuntimeError, match="empty output"):
                gen.run_claude("prompt")


class TestGenerateAiMd:
    @patch("generate_ai_docs.validate_markdown_syntax", return_value=True)
    @patch("generate_ai_docs.run_claude")
    @patch("generate_ai_docs.build_context", return_value="ctx")
    def test_writes_file_on_success(
        self, mock_ctx: MagicMock, mock_claude: MagicMock, mock_syntax: MagicMock, tmp_path: Path
    ) -> None:
        content = "\n".join(f"# {s}" for s in gen.REQUIRED_SECTIONS)
        mock_claude.return_value = content
        with patch.object(gen, "AI_MD_PATH", tmp_path / "AI.md"):
            gen.generate_ai_md()
        assert (tmp_path / "AI.md").read_text() == content

    @patch("generate_ai_docs.run_claude", side_effect=RuntimeError("fail"))
    @patch("generate_ai_docs.build_context", return_value="ctx")
    def test_exits_on_claude_failure(self, mock_ctx: MagicMock, mock_claude: MagicMock) -> None:
        with pytest.raises(SystemExit):
            gen.generate_ai_md()

    @patch("generate_ai_docs.validate_markdown_syntax", return_value=True)
    @patch("generate_ai_docs.run_claude", return_value="# Only Summary")
    @patch("generate_ai_docs.build_context", return_value="ctx")
    def test_does_not_write_on_missing_sections(
        self,
        mock_ctx: MagicMock,
        mock_claude: MagicMock,
        mock_syntax: MagicMock,
        tmp_path: Path,
    ) -> None:
        with patch.object(gen, "AI_MD_PATH", tmp_path / "AI.md"):
            with pytest.raises(SystemExit):
                gen.generate_ai_md()
        assert not (tmp_path / "AI.md").exists()

    @patch("generate_ai_docs.validate_markdown_syntax", return_value=False)
    @patch("generate_ai_docs.run_claude")
    @patch("generate_ai_docs.build_context", return_value="ctx")
    def test_does_not_write_on_syntax_failure(
        self,
        mock_ctx: MagicMock,
        mock_claude: MagicMock,
        mock_syntax: MagicMock,
        tmp_path: Path,
    ) -> None:
        mock_claude.return_value = "\n".join(f"# {s}" for s in gen.REQUIRED_SECTIONS)
        with patch.object(gen, "AI_MD_PATH", tmp_path / "AI.md"):
            with pytest.raises(SystemExit):
                gen.generate_ai_md()
        assert not (tmp_path / "AI.md").exists()


class TestIdempotency:
    """Verify structural idempotency guarantee (T010, US3-AC3)."""

    def test_validate_structure_is_deterministic(self) -> None:
        content = "\n".join(f"# {s}" for s in gen.REQUIRED_SECTIONS)
        assert gen.validate_markdown_structure(content) == []
        assert gen.validate_markdown_structure(content) == []

    def test_current_ai_md_passes_structural_validation(self) -> None:
        ai_md = gen.AI_MD_PATH.read_text(encoding="utf-8")
        missing = gen.validate_markdown_structure(ai_md)
        assert missing == [], f"AI.md missing sections: {missing}"

import argparse
import re
from pathlib import Path
from typing import Optional

from git import Git, GitCommandError, Repo

_git = Git()


def sanitize_branch_name(raw: str) -> str:
    """Return a branch-safe name by stripping/normalizing disallowed characters.

    Raises:
        ValueError: If the sanitized name still fails ``git check-ref-format --branch``
            validation (e.g. contains ``@{`` sequences or other ref-format violations).
    """

    name = raw.strip().lower()
    name = re.sub(r"\s+", "-", name)  # spaces to dashes
    name = re.sub(r"[^a-z0-9._/-]+", "-", name)  # drop invalid chars
    name = re.sub(r"[-/.]{2,}", "-", name)  # collapse repeated separators
    name = name.lstrip("-./").rstrip("-./")  # trim edge separators
    if name.endswith(".lock"):
        name = name[: -len(".lock")]
    name = name or "branch"
    name = name[:250]

    try:
        _git.check_ref_format("--branch", name)
    except GitCommandError:
        raise ValueError(
            f"Sanitized branch name '{name}' is still invalid per git check-ref-format. "
            "Please provide a different name."
        )

    return name


class GitPython:
    """Utility class for Git operations using GitPython library."""

    def __init__(
        self,
        target_branch_name: str,
        base_branch: Optional[str] = None,
        source_ref: str = "HEAD",
        repo_path: str = ".",
    ) -> None:
        """
        Initialize the GitPython utility with the given repository path and branch information.

        Args:
            target_branch_name (str): Name of the target branch to work with. It will be
                sanitized to ensure it is a valid Git branch name.
            base_branch (Optional[str]): Name of the base branch from which the target branch
                will be created. If not provided, the repository's active branch is used.
            source_ref (str): Git reference (e.g., a branch name or commit hash) representing
                the source of changes. Defaults to ``"HEAD"``.
            repo_path (str): Path to the Git repository. Defaults to the current directory
                (``"."``).
        """

        self.repo = Repo(repo_path)
        self.source_ref = source_ref
        self.base_branch = base_branch if base_branch else self.repo.active_branch.name
        self.target_branch_name: str = sanitize_branch_name(target_branch_name)

    def create_branch(self) -> None:
        """Create the target branch."""

        # Check for dirty worktree before attempting to create a branch to avoid losing changes.
        if self.repo.is_dirty(untracked_files=True):
            raise RuntimeError("Worktree dirty; commit/stash before creating a branch.")
        if self.target_branch_name in [b.name for b in self.repo.branches]:
            raise RuntimeError(f"Branch '{self.target_branch_name}' already exists.")

        # Create the branch pointing at the base without checking it out (keeps current branch).
        try:
            self.repo.git.branch(self.target_branch_name, self.base_branch)
            print(
                f"Branch '{self.target_branch_name}' created at '{self.base_branch}' without checkout."
            )
        except GitCommandError as e:
            raise RuntimeError(f"Error creating branch '{self.target_branch_name}': {e}") from e

    def set_upstream(self, remote_name: str = "origin") -> None:
        """Set the upstream for the current branch to the specified remote."""

        try:
            self.repo.git.push("--set-upstream", remote_name, self.target_branch_name)
            print(f"Upstream set for branch '{self.target_branch_name}' to remote '{remote_name}'.")
        except GitCommandError as e:
            raise RuntimeError(
                f"Error setting upstream for branch '{self.target_branch_name}': {e}"
            ) from e

    def commit_changes(self, commit_message: str) -> None:
        """Stage and commit all changes on the target branch."""

        try:
            self.repo.git.add(all=True)
            self.repo.index.commit(commit_message)
            print(f"Changes committed with message: '{commit_message}'")
        except GitCommandError as e:
            raise RuntimeError(f"Error committing changes: {e}") from e

    def push_branch(self, remote_name: str = "origin") -> None:
        """Push the current branch to the specified remote."""

        try:
            self.repo.git.push(remote_name, f"{self.source_ref}:{self.target_branch_name}")
            print(f"Branch '{self.target_branch_name}' pushed to remote '{remote_name}'.")
        except GitCommandError as e:
            raise RuntimeError(f"Error pushing branch '{self.target_branch_name}': {e}") from e

    def log_git(self, remote_name: str = "origin") -> str:
        """Return the Git log for the target branch from ``git log --oneline``.

        If the named remote exists in the repository, it is fetched first so
        the log reflects the latest remote commits.  If the remote is not
        configured the fetch step is silently skipped.

        Args:
            remote_name (str): Name of the remote to fetch from before
                logging.  Defaults to ``"origin"``.

        Returns:
            str: The one-line Git log for the target branch.

        Raises:
            RuntimeError: If the git log command fails.
        """

        try:
            if any(r.name == remote_name for r in self.repo.remotes):
                self.repo.git.fetch(remote_name)
            return str(self.repo.git.log("--oneline", self.target_branch_name))
        except GitCommandError as e:
            raise RuntimeError(f"Error retrieving Git log: {e}") from e


def generate_file_for_commit(
    file_path: str = "spikes/generated/generated_file.txt", content: str = "Generated file"
) -> None:
    """Utility function to generate a file with the given content for committing."""

    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)  # create dirs if needed
    path.touch(exist_ok=True)  # create empty file if it doesn’t exist

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def main() -> None:
    """Main function to demonstrate GitPython utility."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--uuid", required=True, help="UUID for the branch.")
    args = parser.parse_args()

    git_util = GitPython(repo_path=".", target_branch_name=f"codegen/test-{args.uuid}")
    git_util.create_branch()
    generate_file_for_commit(content=f"Generated content for commit {args.uuid}")
    git_util.commit_changes(commit_message=f"Test commit for branch codegen/test-{args.uuid}")
    git_util.push_branch()
    print(git_util.log_git())


if __name__ == "__main__":
    main()

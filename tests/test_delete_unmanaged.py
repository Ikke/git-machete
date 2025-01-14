from typing import Any

from .base_test import BaseTest
from .mockers import (assert_command, fixed_author_and_committer_date,
                      launch_command, mock_ask_if_returning,
                      mock_run_cmd_and_forward_stdout, rewrite_definition_file)


class TestDeleteUnmanaged(BaseTest):

    def test_delete_unmanaged(self, mocker: Any) -> None:
        mocker.patch('git_machete.utils.run_cmd', mock_run_cmd_and_forward_stdout)

        with fixed_author_and_committer_date():
            (
                self.repo_sandbox.new_branch("master")
                    .commit("master commit.")
                    .new_branch("develop")
                    .commit("develop commit.")
                    .new_branch("feature")
                    .commit("feature commit.")
            )
        body: str = \
            """
            master
            """
        rewrite_definition_file(body)

        assert_command(
            ["delete-unmanaged", "--yes"],
            """
            Checking for unmanaged branches...
            Skipping current branch feature
            Deleting branch develop (merged to HEAD)...
            Deleted branch develop (was 03e727b).

            """
        )

        self.repo_sandbox.check_out("master")
        assert_command(
            ["delete-unmanaged", "-y"],
            """
            Checking for unmanaged branches...
            Deleting branch feature (unmerged to HEAD)...
            Deleted branch feature (was 87e00e9).

            """
        )

        assert_command(
            ["delete-unmanaged", "-y"],
            """
            Checking for unmanaged branches...
            No branches to delete
            """
        )

        self.repo_sandbox.new_branch("foo").check_out("master")
        mocker.patch("git_machete.client.MacheteClient.ask_if", mock_ask_if_returning("n"))
        launch_command("delete-unmanaged")
        assert self.repo_sandbox.get_local_branches() == ["foo", "master"]

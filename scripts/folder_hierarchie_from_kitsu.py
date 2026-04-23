import argparse
import getpass
import os
import sys

import gazu


DEFAULT_KITSU_URL = "https://20-stm.cg-wire.com/api"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create folder hierarchy from Kitsu episodes/shots."
    )
    parser.add_argument(
        "--kitsu-url",
        default=DEFAULT_KITSU_URL,
        help=f"Kitsu API base URL (default: {DEFAULT_KITSU_URL}).",
    )
    parser.add_argument(
        "--admin-email",
        default=os.environ.get("ADMIN_EMAIL"),
        help="Kitsu admin email (or env ADMIN_EMAIL).",
    )
    parser.add_argument(
        "--admin-password",
        default=os.environ.get("ADMIN_PASSWORD"),
        help="Kitsu admin password (or env ADMIN_PASSWORD). If omitted, prompts securely.",
    )
    parser.add_argument(
        "--episodes-name",
        nargs="*",
        type=int,
        help="Episode names to process (integers). Example: --episodes-name 143 144",
    )
    parser.add_argument(
        "--project-name",
        default="Melody et Momon",
        help='Kitsu project name (default: "Melody et Momon").',
    )
    parser.add_argument(
        "--dir-path",
        default=r"R:\melodyandmomon\screening",
        help=r'Root directory where episode folders live (default: R:\melodyandmomon\screening).',
    )
    return parser.parse_args()


def _is_interactive() -> bool:
    try:
        return sys.stdin.isatty()
    except Exception:
        return False


def _prompt_if_missing(args: argparse.Namespace) -> tuple[str, str, list[int]]:
    if not args.admin_email:
        if not _is_interactive():
            raise SystemExit("Missing --admin-email (or env ADMIN_EMAIL).")
        args.admin_email = input("Kitsu admin email: ").strip() or None
        if not args.admin_email:
            raise SystemExit("Missing admin email.")

    admin_password = args.admin_password
    if not admin_password:
        if not _is_interactive():
            raise SystemExit("Missing --admin-password (or env ADMIN_PASSWORD).")
        admin_password = getpass.getpass("Kitsu admin password: ")

    episodes_name = args.episodes_name
    if not episodes_name:
        if not _is_interactive():
            raise SystemExit("Missing --episodes-name (at least one integer).")
        raw = input("Episodes (space/comma separated integers): ").strip()
        tokens = [t for t in raw.replace(",", " ").split(" ") if t]
        try:
            episodes_name = [int(t) for t in tokens]
        except ValueError:
            raise SystemExit("Invalid episodes list: must be integers.") from None

    if not isinstance(episodes_name, list) or len(episodes_name) < 1:
        raise SystemExit("--episodes-name must contain at least one integer.")

    return args.admin_email, admin_password, episodes_name


def main() -> int:
    args = _parse_args()
    ADMIN_EMAIL, ADMIN_PASSWORD, episodes_name = _prompt_if_missing(args)
    episodes_name_set = set(episodes_name)

    gazu.set_host(args.kitsu_url)
    gazu.log_in(ADMIN_EMAIL, ADMIN_PASSWORD)
    print("Connected to Kitsu via gazu.")

    projects = gazu.project.all_projects()
    project = next((p for p in projects if p.get("name") == args.project_name), None)
    if not project:
        raise SystemExit(f'Project not found in Kitsu: "{args.project_name}"')

    episodes = gazu.context.all_episodes_for_project(project)

    if not os.path.isdir(args.dir_path):
        raise SystemExit(f"Directory does not exist: {args.dir_path}")

    subdirectories = [
        name
        for name in os.listdir(args.dir_path)
        if os.path.isdir(os.path.join(args.dir_path, name))
    ]

    for episode in episodes:
        episode_folder_name = episode.get("name")
        if not episode_folder_name or episode_folder_name not in subdirectories:
            continue

        try:
            episode_number = int(episode_folder_name)
        except (TypeError, ValueError):
            continue

        if episode_number not in episodes_name_set:
            continue

        ep_dir = os.path.join(args.dir_path, episode_folder_name)
        scenes_dir = os.path.join(ep_dir, "Scenes")

        if not os.path.exists(scenes_dir) and os.path.exists(os.path.join(ep_dir, "Scene")):
            os.rename(os.path.join(ep_dir, "Scene"), scenes_dir)

        sequence_dir = os.path.join(scenes_dir, "001")
        if not os.path.exists(sequence_dir) and os.path.exists(os.path.join(scenes_dir, "0001")):
            os.rename(os.path.join(scenes_dir, "0001"), sequence_dir)
        os.makedirs(sequence_dir, exist_ok=True)

        for shot in gazu.shot.all_shots_for_episode(episode):
            shot_name = shot.get("name")
            if not shot_name:
                continue

            if shot_name not in os.listdir(sequence_dir):
                os.makedirs(os.path.join(sequence_dir, shot_name), exist_ok=True)

            shot_dir = os.path.join(sequence_dir, shot_name)
            anim_dir = os.path.join(shot_dir, "Animation")
            layout_dir = os.path.join(shot_dir, "Lay")

            tasks = [task for task in gazu.context.all_task_types_for_shot(shot)]
            for task in tasks:
                task_dir = None
                department = gazu.person.get_department(task["department_id"])

                if department["name"] == "Animation":
                    if task["name"] == "Spline":
                        if not os.path.exists(os.path.join(anim_dir, task["name"])):
                            task_dir = os.path.join(anim_dir, task["name"])
                elif department["name"] == "Layout":
                    task_dir = layout_dir
                elif department["name"] == "Compositing":
                    if task["name"] == "Rendering":
                        task_dir = os.path.join(shot_dir, "Compositing", "CO")
                    elif task["name"] == "Lighting":
                        task_dir = os.path.join(shot_dir, "Lighting")

                if task_dir:
                    os.makedirs(task_dir, exist_ok=True)
                    print(
                        f"Created directory for task {task['name']} in {task_dir}, for department {department['name']}"
                    )

            finaling_dir = os.path.join(shot_dir, "Pre_Finaling")
            os.makedirs(finaling_dir, exist_ok=True)
            print(f"Created directory for task in {finaling_dir}, for department Finaling")

            publish_dir = os.path.join(shot_dir, "Publish")
            cache_dir = os.path.join(publish_dir, "cache")
            os.makedirs(cache_dir, exist_ok=True)
            print(f"Created directory for task in {publish_dir}, for department Publish")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


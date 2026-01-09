"""Display utilities for pipeline execution visualization."""

import sys
from dataclasses import dataclass, field
from typing import List, Optional


# ANSI Colors
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    BLACK = "\033[30m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"

    BG_GREEN = "\033[42m"
    BG_RED = "\033[41m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"


BANNER = r"""
  ____  _            _ _              _____                     _
 |  _ \(_)_ __   ___| (_)_ __   ___  | ____|_  _____  ___ _   _| |_ ___  _ __
 | |_) | | '_ \ / _ \ | | '_ \ / _ \ |  _| \ \/ / _ \/ __| | | | __/ _ \| '__|
 |  __/| | |_) |  __/ | | | | |  __/ | |___ >  <  __/ (__| |_| | || (_) | |
 |_|   |_| .__/ \___|_|_|_| |_|\___| |_____/_/\_\___|\___|\__,_|\__\___/|_|
         |_|
"""


@dataclass
class StepResult:
    """Result of a single pipeline step."""
    name: str
    job: str
    success: bool
    message: Optional[str] = None
    duration: float = 0.0


@dataclass
class PipelineStats:
    """Statistics for pipeline execution."""
    total_steps: int = 0
    completed_steps: int = 0
    successful_steps: int = 0
    failed_steps: int = 0
    skipped_steps: int = 0
    results: List[StepResult] = field(default_factory=list)

    def add_result(self, result: StepResult):
        self.results.append(result)
        self.completed_steps += 1
        if result.success:
            self.successful_steps += 1
        else:
            self.failed_steps += 1


class Display:
    """Handles all visual output for the pipeline."""

    @staticmethod
    def banner(version: str, debug: bool = False):
        """Print startup banner with config info."""
        print(f"{Colors.CYAN}{BANNER}{Colors.RESET}")
        print(f"{Colors.DIM}{'─' * 60}{Colors.RESET}")
        print(f"  {Colors.BOLD}Version:{Colors.RESET} {version}")
        print(f"  {Colors.BOLD}Debug:{Colors.RESET}   {'enabled' if debug else 'disabled'}")
        print(f"{Colors.DIM}{'─' * 60}{Colors.RESET}")
        print()

    @staticmethod
    def pipeline_start(pipeline_file: str, total_steps: int):
        """Print pipeline start info."""
        print(f"{Colors.BLUE}{Colors.BOLD}Pipeline:{Colors.RESET} {pipeline_file}")
        print(f"{Colors.BLUE}{Colors.BOLD}Steps:{Colors.RESET}    {total_steps}")
        print()
        print(f"{Colors.DIM}{'─' * 60}{Colors.RESET}")

    @staticmethod
    def step_start(step_num: int, total: int, name: str, job: str):
        """Print step start with progress indicator."""
        progress = f"[{step_num}/{total}]"
        bar_width = 20
        filled = int(bar_width * step_num / total)
        bar = "█" * filled + "░" * (bar_width - filled)

        print(f"\n{Colors.CYAN}{progress}{Colors.RESET} {bar} {Colors.BOLD}{name}{Colors.RESET}")
        print(f"    {Colors.DIM}Job: {job}{Colors.RESET}")

    @staticmethod
    def step_result(success: bool, message: Optional[str] = None, duration: float = 0.0):
        """Print step result."""
        if success:
            status = f"{Colors.GREEN}✓ SUCCESS{Colors.RESET}"
        else:
            status = f"{Colors.RED}✗ FAILED{Colors.RESET}"

        duration_str = f"{Colors.DIM}({duration:.2f}s){Colors.RESET}" if duration > 0 else ""
        print(f"    {status} {duration_str}")

        if message and not success:
            print(f"    {Colors.RED}{message}{Colors.RESET}")

    @staticmethod
    def step_skipped(step_num: int, total: int, name: str):
        """Print skipped step."""
        progress = f"[{step_num}/{total}]"
        print(f"\n{Colors.DIM}{progress} {name} - SKIPPED{Colors.RESET}")

    @staticmethod
    def dynamic_iteration(current: int, total: int, params: dict):
        """Print dynamic iteration progress."""
        print(f"      {Colors.DIM}Iteration {current}/{total}{Colors.RESET}", end="")
        sys.stdout.flush()

    @staticmethod
    def dynamic_iteration_result(success: bool):
        """Print dynamic iteration result inline."""
        if success:
            print(f" {Colors.GREEN}✓{Colors.RESET}")
        else:
            print(f" {Colors.RED}✗{Colors.RESET}")

    @staticmethod
    def summary(stats: PipelineStats, duration: float):
        """Print final pipeline summary."""
        print()
        print(f"{Colors.DIM}{'─' * 60}{Colors.RESET}")
        print()

        if stats.failed_steps == 0:
            header = f"{Colors.BG_GREEN}{Colors.BLACK}{Colors.BOLD} PIPELINE SUCCESSFUL {Colors.RESET}"
        else:
            header = f"{Colors.BG_RED}{Colors.WHITE}{Colors.BOLD} PIPELINE FAILED {Colors.RESET}"

        print(f"  {header}")
        print()
        print(f"  {Colors.BOLD}Summary:{Colors.RESET}")
        print(f"    Total Steps:   {stats.total_steps}")
        print(f"    {Colors.GREEN}Successful:{Colors.RESET}    {stats.successful_steps}")
        if stats.failed_steps > 0:
            print(f"    {Colors.RED}Failed:{Colors.RESET}        {stats.failed_steps}")
        if stats.skipped_steps > 0:
            print(f"    {Colors.YELLOW}Skipped:{Colors.RESET}       {stats.skipped_steps}")
        print(f"    {Colors.BOLD}Duration:{Colors.RESET}      {duration:.2f}s")
        print()

        # Show failed steps details
        failed = [r for r in stats.results if not r.success]
        if failed:
            print(f"  {Colors.RED}{Colors.BOLD}Failed Steps:{Colors.RESET}")
            for r in failed:
                print(f"    - {r.name}: {r.message or 'Unknown error'}")
            print()

        print(f"{Colors.DIM}{'─' * 60}{Colors.RESET}")

    @staticmethod
    def curl_command(method: str, url: str, headers: dict, body: dict = None, masked: bool = True):
        """Print a copyable CURL command."""
        print()
        print(f"    {Colors.DIM}┌─ CURL Command ─────────────────────────{Colors.RESET}")

        parts = [f"curl -X {method}"]

        for key, value in headers.items():
            if masked and key.lower() in ("authorization", "x-api-key"):
                value = "$API_TOKEN"  # Use env var placeholder
            parts.append(f"-H '{key}: {value}'")

        if body:
            import json
            body_str = json.dumps(body)
            parts.append(f"-d '{body_str}'")

        parts.append(f"'{url}'")

        # Format for display
        curl_str = " \\\n      ".join(parts)
        print(f"    {Colors.DIM}│{Colors.RESET} {Colors.YELLOW}{curl_str}{Colors.RESET}")
        print(f"    {Colors.DIM}└────────────────────────────────────────{Colors.RESET}")

    @staticmethod
    def api_call(method: str, endpoint: str, show_curl: bool = False,
                 url: str = None, headers: dict = None, body: dict = None):
        """Print API call info with optional CURL command."""
        method_colors = {
            "GET": Colors.GREEN,
            "POST": Colors.BLUE,
            "PUT": Colors.YELLOW,
            "DELETE": Colors.RED,
        }
        color = method_colors.get(method, Colors.WHITE)
        print(f"      {Colors.DIM}API:{Colors.RESET} {color}{method}{Colors.RESET} {endpoint}")

        if show_curl and url and headers:
            Display.curl_command(method, url, headers, body)

    @staticmethod
    def inputs_overview(inputs: dict, debug: bool = False):
        """Print a formatted overview of loaded inputs."""
        print()
        print(f"  {Colors.MAGENTA}{Colors.BOLD}Loaded Inputs{Colors.RESET}")
        print(f"  {Colors.DIM}{'─' * 40}{Colors.RESET}")

        if not inputs:
            print(f"  {Colors.DIM}No inputs loaded{Colors.RESET}")
            print()
            return

        for key, value in inputs.items():
            if isinstance(value, list):
                count = len(value)
                icon = "📦" if "org" in key.lower() else "🤖" if "robot" in key.lower() else "📋"
                print(f"  {icon} {Colors.BOLD}{key}{Colors.RESET} ({Colors.CYAN}{count}{Colors.RESET} items)")

                if debug:
                    # Show detailed list in debug mode
                    for i, item in enumerate(value, 1):
                        if isinstance(item, dict):
                            # Get the most important identifier
                            name = item.get("name") or item.get("robot_shortname") or item.get("id") or f"Item {i}"
                            print(f"      {Colors.DIM}{i}.{Colors.RESET} {Colors.GREEN}{name}{Colors.RESET}")
                            # Show other fields
                            for k, v in item.items():
                                if k not in ["name", "robot_shortname", "id"]:
                                    val_str = str(v)[:30] + "..." if len(str(v)) > 30 else str(v)
                                    print(f"         {Colors.DIM}{k}: {val_str}{Colors.RESET}")
                        else:
                            print(f"      {Colors.DIM}{i}.{Colors.RESET} {item}")
                else:
                    # Compact view: just show names
                    names = []
                    for item in value[:5]:  # Show max 5
                        if isinstance(item, dict):
                            name = item.get("name") or item.get("robot_shortname") or "?"
                            names.append(name)
                        else:
                            names.append(str(item))

                    names_str = ", ".join(names)
                    if len(value) > 5:
                        names_str += f", ... (+{len(value) - 5} more)"
                    print(f"      {Colors.DIM}→ {names_str}{Colors.RESET}")

                print()
            else:
                # Single value
                print(f"  📌 {Colors.BOLD}{key}{Colors.RESET}: {value}")
                print()

        print(f"  {Colors.DIM}{'─' * 40}{Colors.RESET}")
        print()

    @staticmethod
    def pipeline_overview(pipeline, debug: bool = False):
        """Print pipeline structure overview."""
        steps = pipeline.pipeline
        enabled = [s for s in steps if s.enabled]
        disabled = [s for s in steps if not s.enabled]

        print()
        print(f"  {Colors.CYAN}{Colors.BOLD}Pipeline Overview{Colors.RESET}")
        print(f"  {Colors.DIM}{'─' * 40}{Colors.RESET}")

        for i, step in enumerate(steps, 1):
            if step.enabled:
                status = f"{Colors.GREEN}●{Colors.RESET}"
                name_style = Colors.BOLD
            else:
                status = f"{Colors.DIM}○{Colors.RESET}"
                name_style = Colors.DIM

            # Step name and job
            print(f"  {status} {name_style}{step.name}{Colors.RESET}")
            print(f"      {Colors.DIM}Job:{Colors.RESET} {step.job}")

            # Show params info
            if step.params_list:
                key = step.params_list.replace("{{ ", "").replace(" }}", "")
                print(f"      {Colors.CYAN}↻{Colors.RESET} Dynamic: {Colors.CYAN}{key}{Colors.RESET}")
            elif step.params:
                param_count = len(step.params)
                print(f"      {Colors.DIM}Params: {param_count} parameter(s){Colors.RESET}")

            # Debug: show all param details
            if debug and step.params:
                for k, v in step.params.items():
                    val_str = str(v)[:50] + "..." if len(str(v)) > 50 else str(v)
                    print(f"        {Colors.DIM}• {k}: {val_str}{Colors.RESET}")

            if debug and step.params_list:
                print(f"        {Colors.DIM}• template: {step.params_list}{Colors.RESET}")

            print()

        # Summary line
        print(f"  {Colors.DIM}{'─' * 40}{Colors.RESET}")
        summary = f"  {Colors.GREEN}{len(enabled)} enabled{Colors.RESET}"
        if disabled:
            summary += f" {Colors.DIM}| {len(disabled)} disabled{Colors.RESET}"
        print(summary)
        print()

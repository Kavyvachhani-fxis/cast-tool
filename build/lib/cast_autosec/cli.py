
import argparse, os, sys, subprocess, json, shutil, textwrap
from pathlib import Path
import yaml
from .jenkinsfile import generate_jenkinsfile
from .reporting import combine_reports
from .util import ensure_workspace, run_cmd, docker_available

DEFAULTS_PATH = Path(__file__).with_name("config.example.yaml")

def load_config(cfg_path: str | None):
    cfg = yaml.safe_load(DEFAULTS_PATH.read_text())
    if cfg_path and Path(cfg_path).exists():
        user_cfg = yaml.safe_load(Path(cfg_path).read_text())
        # shallow merge
        for k,v in user_cfg.items():
            cfg[k] = v
    return cfg

def cmd_init(args):
    ws = ensure_workspace(args.workspace)
    cfg_dst = ws/"config.yaml"
    if not cfg_dst.exists():
        cfg_dst.write_text(Path(DEFAULTS_PATH).read_text())
    print(f"Workspace ready at {ws}")
    print(f"Edit config at {cfg_dst}")

def cmd_gen_jenkins(args):
    jfile = generate_jenkinsfile(args.github_url, sonar_url=args.sonar_url)
    Path(args.out).write_text(jfile)
    print(f"Jenkinsfile written to {args.out}")

def cmd_scan(args):
    cfg = load_config(args.config)
    ws = ensure_workspace(cfg.get("workspace"))
    out_dir = ws/ cfg.get("reports",{}).get("out_dir","reports")
    out_dir.mkdir(parents=True, exist_ok=True)

    if not docker_available():
        print("Docker not available; cannot run containerized scanners.", file=sys.stderr)
        sys.exit(2)

    # Dependency-Check
    dc_out = out_dir/"dependency-check-report.html"
    src = Path(args.path).resolve()
    run_cmd(["docker","run","--rm","-v",f"{src}:/src","-v",f"{out_dir}:/report",
             cfg["tools"]["dependency_check"]["image"],
             "--project", cfg["reports"]["project_name"], "--scan","/src","--out","/report","--format","ALL"])

    # Trivy
    trivy_json = out_dir/"trivy.json"
    run_cmd(["docker","run","--rm","-v",f"{src}:/src","-v",f"{out_dir}:/out",
             cfg["tools"]["trivy"]["image"],"fs","--security-checks","vuln,config",
             "--severity","HIGH,CRITICAL","--format","json","-o","/out/trivy.json","/src"])

    print("Scans finished. Reports in", out_dir)

def cmd_report(args):
    ws = ensure_workspace(None)
    combine_reports(Path(args.reports_dir), Path(args.output))
    print(f"Combined PDF at {args.output}")

def main(argv=None):
    p = argparse.ArgumentParser(prog="cast-autosec", description="CAST AutoSec CLI")
    sub = p.add_subparsers(required=True)

    sp = sub.add_parser("init", help="create workspace & default config")
    sp.add_argument("--workspace", default=None)
    sp.set_defaults(func=cmd_init)

    sp = sub.add_parser("gen-jenkins", help="generate Jenkinsfile from GitHub URL")
    sp.add_argument("github_url")
    sp.add_argument("--sonar-url", default="http://localhost:9000")
    sp.add_argument("--out", default="Jenkinsfile")
    sp.set_defaults(func=cmd_gen_jenkins)

    sp = sub.add_parser("scan", help="run dependency-check and trivy via Docker")
    sp.add_argument("--config", default=None)
    sp.add_argument("--path", default=".")
    sp.set_defaults(func=cmd_scan)

    sp = sub.add_parser("report", help="combine produced reports into one PDF")
    sp.add_argument("--reports-dir", default="reports")
    sp.add_argument("--output", default="cast_autosec_report.pdf")
    sp.set_defaults(func=cmd_report)

    args = p.parse_args(argv)
    args.func(args)

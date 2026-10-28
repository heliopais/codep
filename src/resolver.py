#!/usr/bin/env python3
"""
codep resolver: smart, multi-token and fuzzy project directory matcher.
Part of codep (https://github.com/heliopais/codep)
"""

import os
import sys
import json
import difflib
import subprocess

DEFAULT_SEARCH_ROOTS = [
    "~/repos",
    "~/Documents",
    "~/Projects",
    "~/Developer",
    "~/Code",
    "~/workspace",
    "~/src",
]

DEFAULT_IGNORED_DIRS = {
    ".git", ".venv", "venv", "env", ".env", "node_modules", "dist", "build",
    "__pycache__", ".cache", ".next", ".dolt", "Library", "Applications",
    ".gemini", ".claude", ".codex", ".local", "site-packages", "standalone-env",
    ".idea", ".vscode", ".tox", "Pods", "Carthage", ".terraform", "target",
    ".beads", ".beads-planning", ".ruff_cache", ".pytest_cache"
}

def load_config():
    """Load configuration from ~/.config/codep/config.json or environment."""
    config = {
        "search_roots": [],
        "ignored_dirs": list(DEFAULT_IGNORED_DIRS),
        "editor": os.environ.get("CODEP_EDITOR", "Visual Studio Code"),
        "max_depth": 3,
    }
    
    config_path = os.environ.get(
        "CODEP_CONFIG",
        os.path.expanduser("~/.config/codep/config.json")
    )
    if os.path.isfile(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                user_cfg = json.load(f)
                if "search_roots" in user_cfg:
                    config["search_roots"] = user_cfg["search_roots"]
                if "ignored_dirs" in user_cfg:
                    config["ignored_dirs"] = user_cfg["ignored_dirs"]
                if "editor" in user_cfg:
                    config["editor"] = user_cfg["editor"]
                if "max_depth" in user_cfg:
                    config["max_depth"] = user_cfg["max_depth"]
        except Exception as e:
            sys.stderr.write(f"Warning: Could not read config {config_path}: {e}\n")

    # If search_roots is empty, check environment or use defaults
    if not config["search_roots"]:
        env_roots = os.environ.get("CODEP_SEARCH_ROOTS")
        if env_roots:
            config["search_roots"] = [r.strip() for r in env_roots.split(":") if r.strip()]
        else:
            config["search_roots"] = [
                r for r in DEFAULT_SEARCH_ROOTS if os.path.isdir(os.path.expanduser(r))
            ]
            
    # Normalize paths
    config["search_roots"] = [os.path.expanduser(r) for r in config["search_roots"]]
    config["ignored_dirs"] = set(config["ignored_dirs"])
    return config

def get_candidate_folders(search_roots, ignored_dirs, max_depth=3):
    """Walk search roots up to max_depth, ignoring noisy directories."""
    candidates = []
    for root in search_roots:
        if not os.path.isdir(root):
            continue
        for dirpath, dirnames, _ in os.walk(root):
            # In-place filtering of ignored dirs
            dirnames[:] = [d for d in dirnames if not d.startswith(".") and d not in ignored_dirs]
            rel = os.path.relpath(dirpath, root)
            depth = len(rel.split(os.sep)) if rel != "." else 0
            if depth > max_depth:
                dirnames.clear()
                continue
            if depth > 0:
                candidates.append(dirpath)
    return candidates

def score_candidate(path, tokens, raw_query):
    """Score a folder path against search tokens and raw query."""
    basename = os.path.basename(path).lower()
    full_lower = path.lower()
    clean_base = basename.replace("-", " ").replace("_", " ")

    token_base_hits = sum(1 for t in tokens if t in basename or t in clean_base)
    token_path_hits = sum(1 for t in tokens if t in full_lower)

    all_in_path = (token_path_hits == len(tokens))
    all_in_base = (token_base_hits == len(tokens))

    score = 0.0

    if all_in_path:
        score += 1000.0
        if all_in_base:
            score += 500.0

        if clean_base == raw_query or basename == raw_query:
            score += 400.0
        elif raw_query in clean_base:
            score += 250.0
        elif all(t in clean_base.split() for t in tokens):
            score += 200.0

        # Prioritize Git repo roots
        if os.path.isdir(os.path.join(path, ".git")):
            score += 120.0

        # Slight penalty for deep nesting and excessive length
        score -= len(basename) * 0.4
        rel_depth = len(path.split(os.sep))
        score -= rel_depth * 5.0
    else:
        # Partial token hits
        score += token_path_hits * 120.0
        score += token_base_hits * 80.0

        # Fuzzy string similarity
        r_base = difflib.SequenceMatcher(None, raw_query, basename).ratio()
        r_clean = difflib.SequenceMatcher(None, raw_query, clean_base).ratio()
        best_ratio = max(r_base, r_clean)
        score += best_ratio * 150.0

        if os.path.isdir(os.path.join(path, ".git")):
            score += 40.0

    return score, all_in_path

def to_user_path(p):
    """Convert absolute path to ~/relative for clean UI display."""
    home = os.path.expanduser("~")
    if p.startswith(home):
        return "~" + p[len(home):]
    return p

def resolve(query, config=None, candidate_override=None):
    """
    Resolve query string to (mode, list_of_paths).
    Modes:
      - 'SINGLE': 1 clear winner path
      - 'MULTIPLE': list of paths matching all tokens
      - 'APPROX': list of approximate/fuzzy matches
      - 'NONE': no candidates found
    """
    query = query.strip()
    if not query:
        return "NONE", []

    # Direct existing path
    expanded = os.path.expanduser(query)
    if os.path.isdir(expanded):
        return "SINGLE", [os.path.abspath(expanded)]

    if config is None:
        config = load_config()

    raw_query = query.lower()
    tokens = [t.lower() for t in query.replace("-", " ").replace("_", " ").split() if t.strip()]
    if not tokens:
        return "NONE", []

    candidates = candidate_override
    if candidates is None:
        candidates = get_candidate_folders(
            config["search_roots"],
            config["ignored_dirs"],
            config["max_depth"]
        )

    scored = []
    for p in candidates:
        s, all_matched = score_candidate(p, tokens, raw_query)
        scored.append((s, all_matched, p))

    scored.sort(key=lambda x: x[0], reverse=True)

    all_match_candidates = [item for item in scored if item[1]]

    if all_match_candidates:
        if len(all_match_candidates) == 1:
            return "SINGLE", [all_match_candidates[0][2]]

        top_score = all_match_candidates[0][0]
        second_score = all_match_candidates[1][0]

        # Check for clear dominant winner
        if top_score - second_score >= 120:
            return "SINGLE", [all_match_candidates[0][2]]
        else:
            return "MULTIPLE", [to_user_path(item[2]) for item in all_match_candidates[:12]]
    else:
        # Approximate fuzzy matching
        top_approx = [item for item in scored if item[0] >= 60][:10]
        if top_approx:
            return "APPROX", [to_user_path(item[2]) for item in top_approx]
        else:
            return "NONE", []

if __name__ == "__main__":
    cfg = load_config()
    q = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""
    mode, paths = resolve(q, config=cfg)
    print(f"EDITOR:{cfg['editor']}")
    print(f"MODE:{mode}")
    for p in paths:
        print(p)

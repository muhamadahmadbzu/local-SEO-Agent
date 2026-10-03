#!/usr/bin/env bash
# Install Local SEO Agent for Claude Code (macOS / Linux / WSL).
#
#   bash install.sh                      # clone/update into ~/local-SEO-Agent, verify, done
#   bash install.sh --global             # also make the 14 agents + 11 skills available in every folder
#   bash install.sh --census             # also download official Census city data (needs internet)
#   bash install.sh --dir ~/work/seo     # choose the install folder
#   bash install.sh --no-claude          # don't offer to install Claude Code
#
# One-liner (works when the GitHub repo is public):
#   curl -fsSL https://raw.githubusercontent.com/muhamadahmadbzu/local-SEO-Agent/main/install.sh | bash -s -- --global
set -euo pipefail

REPO_URL="https://github.com/muhamadahmadbzu/local-SEO-Agent.git"
BRANCH="main"
DIR="$HOME/local-SEO-Agent"
GLOBAL=0
CENSUS=0
INSTALL_CLAUDE=1

while [ $# -gt 0 ]; do
  case "$1" in
    --dir) DIR="$2"; shift 2 ;;
    --branch) BRANCH="$2"; shift 2 ;;
    --global) GLOBAL=1; shift ;;
    --census) CENSUS=1; shift ;;
    --no-claude) INSTALL_CLAUDE=0; shift ;;
    -h|--help) sed -n '2,13p' "$0"; exit 0 ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

say()  { printf '\033[1;32m==>\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m!!\033[0m %s\n' "$*"; }
die()  { printf '\033[1;31mxx\033[0m %s\n' "$*" >&2; exit 1; }

# ---------------------------------------------------------------- prerequisites
command -v git >/dev/null 2>&1 || die "git is not installed. Get it from https://git-scm.com/downloads and re-run."

PY=""
for c in python3 python; do
  if command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)' 2>/dev/null; then
    PY="$c"; break
  fi
done
[ -n "$PY" ] || die "Python 3.9+ is required. Install it from https://www.python.org/downloads/ and re-run."
say "Python: $($PY --version 2>&1)"

if command -v claude >/dev/null 2>&1; then
  say "Claude Code: $(claude --version 2>/dev/null | head -n1)"
elif [ "$INSTALL_CLAUDE" -eq 1 ] && command -v npm >/dev/null 2>&1; then
  printf 'Claude Code is not installed. Install it now with npm? [y/N] '
  read -r answer </dev/tty || answer="n"
  if [ "${answer:-n}" = "y" ] || [ "${answer:-n}" = "Y" ]; then
    npm install -g @anthropic-ai/claude-code || warn "npm install failed - see https://code.claude.com/docs/en/setup"
  else
    warn "Skipped. Install later: npm install -g @anthropic-ai/claude-code"
  fi
else
  warn "Claude Code not found. Install it: https://code.claude.com/docs/en/setup (needs Node.js 18+ for npm install)"
fi

# ---------------------------------------------------------------- get the code
if [ -d "$DIR/.git" ]; then
  say "Updating existing install in $DIR"
  git -C "$DIR" fetch --quiet origin "$BRANCH"
  if [ -n "$(git -C "$DIR" status --porcelain -- . ':!projects')" ]; then
    warn "Local changes found outside projects/ - skipping update so nothing is overwritten."
  else
    git -C "$DIR" checkout --quiet "$BRANCH"
    git -C "$DIR" pull --quiet --ff-only origin "$BRANCH" || warn "Could not fast-forward; update manually with git pull."
  fi
elif [ -e "$DIR" ]; then
  die "$DIR exists but is not a git checkout. Use --dir to pick another folder."
else
  say "Cloning into $DIR"
  git clone --quiet --branch "$BRANCH" "$REPO_URL" "$DIR" \
    || die "Clone failed. If the repo is private, sign in first (gh auth login, or a GitHub token) and re-run."
fi
cd "$DIR"

# ---------------------------------------------------------------- verify
AGENTS=$(ls .claude/agents/*.md 2>/dev/null | wc -l | tr -d ' ')
SKILLS=$(ls -d .claude/skills/*/ 2>/dev/null | wc -l | tr -d ' ')
say "Found $AGENTS agents and $SKILLS skills"
say "Running self-tests..."
if "$PY" -m unittest discover -s tests >/tmp/local-seo-agent-tests.log 2>&1; then
  say "Tests passed"
else
  warn "Some tests failed - see /tmp/local-seo-agent-tests.log (the agents still work)."
fi

# ---------------------------------------------------------------- optional: global agents & skills
if [ "$GLOBAL" -eq 1 ]; then
  mkdir -p "$HOME/.claude/agents" "$HOME/.claude/skills"
  for f in .claude/agents/*.md; do
    ln -sfn "$DIR/$f" "$HOME/.claude/agents/$(basename "$f")"
  done
  for d in .claude/skills/*/; do
    name=$(basename "$d")
    target="$HOME/.claude/skills/$name"
    if [ -e "$target" ] && [ ! -L "$target" ]; then
      warn "Skipping skill $name: $target already exists and is not ours"
      continue
    fi
    ln -sfn "$DIR/.claude/skills/$name" "$target"
  done
  say "Linked agents and skills into ~/.claude (they update when you re-run this installer)"
  warn "The helper scripts live in $DIR - start Claude there for project work."
fi

# ---------------------------------------------------------------- optional: Census data
if [ "$CENSUS" -eq 1 ]; then
  say "Downloading official Census city data (a few minutes)..."
  "$PY" scripts/fetch_census_data.py || warn "Census download failed; the bundled GeoNames city list will be used."
fi

cat <<EOF

$(printf '\033[1;32m')Local SEO Agent is installed.$(printf '\033[0m')

  cd "$DIR"
  claude

Then inside Claude Code:
  /agents                      -> see the 14-agent team
  /rank-and-rent discover      -> find niches and cities worth building

Optional:
  python3 scripts/fetch_census_data.py          official Census city data (or re-run with --census)
  export DATAFORSEO_LOGIN=... DATAFORSEO_PASSWORD=...   live search volumes
EOF

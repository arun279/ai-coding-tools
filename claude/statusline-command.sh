#!/bin/bash

# Read JSON input from stdin
INPUT=$(cat)

# Parse JSON using Python and calculate context from transcript
read -r FOLDER MODEL_ID TRANSCRIPT CONTEXT_USED CONTEXT_LIMIT <<< $(echo "$INPUT" | python3 -c "
import sys, json, os

try:
    data = json.load(sys.stdin)
    folder = data.get('workspace', {}).get('current_dir', '')
    model_id = data.get('model', {}).get('id', data.get('model', {}).get('display_name', 'unknown'))
    transcript = data.get('transcript_path', '')

    # Calculate context from transcript file
    context_used = 0
    context_limit = 200000  # Default limit

    # Determine model context limit
    if 'sonnet-4' in model_id.lower():
        context_limit = 200000
    elif 'opus' in model_id.lower():
        context_limit = 200000

    # Read transcript to calculate context usage
    if transcript and os.path.exists(transcript):
        try:
            with open(transcript, 'r') as f:
                lines = f.readlines()
                # Parse JSONL backwards to find most recent main chain entry
                for line in reversed(lines):
                    try:
                        entry = json.loads(line.strip())
                        # Skip sidechain entries
                        if entry.get('isSidechain') == True:
                            continue
                        # Look for message.usage
                        if 'message' in entry and 'usage' in entry['message']:
                            usage = entry['message']['usage']
                            # Context = input_tokens + cache tokens
                            context_used = (
                                usage.get('input_tokens', 0) +
                                usage.get('cache_read_input_tokens', 0) +
                                usage.get('cache_creation_input_tokens', 0)
                            )
                            break
                    except:
                        continue
        except:
            pass

    # Add autocompact buffer to show space until autocompact triggers
    # Autocompact triggers at ~95% capacity, leaving ~10% as buffer
    # This matches /context behavior of showing "used" space including buffer
    autocompact_buffer = int(context_limit * 0.225)  # 22.5% buffer (~45k for 200k)
    context_used_with_buffer = context_used + autocompact_buffer

    print(f'{folder} {model_id} {transcript} {context_used_with_buffer} {context_limit}')
except:
    print('     unknown  0 0')
" 2>/dev/null)

# Get current folder
if [ -z "$FOLDER" ] || [ "$FOLDER" = "" ]; then
    FOLDER=$(pwd)
fi
FOLDER_NAME=$(basename "$FOLDER")

# ANSI color codes
RESET="\e[0m"
BOLD="\e[1m"

# Background colors
BG_DARKBLUE="\e[48;5;25m"
BG_GREEN="\e[42m"
BG_RED="\e[41m"
BG_YELLOW="\e[43m"
BG_PURPLE="\e[45m"
BG_GRAY="\e[48;5;240m"

# Foreground colors
FG_WHITE="\e[97m"
FG_BLACK="\e[30m"
FG_DARKBLUE="\e[38;5;25m"
FG_GREEN="\e[32m"
FG_RED="\e[31m"
FG_YELLOW="\e[33m"
FG_PURPLE="\e[35m"
FG_GRAY="\e[38;5;240m"

# Powerline separator
SEP=""

# Check for git branch and status (simplified - just clean or dirty)
GIT_BRANCH=""
GIT_STATUS="✓"
GIT_BG="$BG_GREEN"
if git rev-parse --git-dir > /dev/null 2>&1; then
    BRANCH=$(git --no-optional-locks branch --show-current 2>/dev/null)
    if [ -n "$BRANCH" ]; then
        GIT_BRANCH="$BRANCH"
        # Check if working directory is clean
        if ! git diff-index --quiet HEAD -- 2>/dev/null; then
            GIT_STATUS="●"
            GIT_BG="$BG_RED"
        fi
    fi
fi

# Simplify model name for display
case "$MODEL_ID" in
    *"claude-sonnet-4"*)
        MODEL_DISPLAY="Sonnet 4"
        ;;
    *"claude-sonnet-3-5"* | *"claude-3-5-sonnet"*)
        MODEL_DISPLAY="Sonnet 3.5"
        ;;
    *"claude-opus"*)
        MODEL_DISPLAY="Opus"
        ;;
    *)
        MODEL_DISPLAY="$MODEL_ID"
        ;;
esac

# Calculate context percentage and determine warning state
CONTEXT_PCT=0
CONTEXT_PREFIX=""
CONTEXT_BG="$BG_GRAY"
CONTEXT_FG="$FG_WHITE"
CONTEXT_STYLE=""

if [ "$CONTEXT_LIMIT" -gt 0 ] && [ "$CONTEXT_USED" -gt 0 ]; then
    CONTEXT_PCT=$(echo "scale=0; ($CONTEXT_USED * 100) / $CONTEXT_LIMIT" | bc)

    # Format context numbers
    if [ "$CONTEXT_USED" -ge 1000 ]; then
        CONTEXT_USED_K=$(echo "scale=0; $CONTEXT_USED / 1000" | bc)
        CONTEXT_USED_DISPLAY="${CONTEXT_USED_K}k"
    else
        CONTEXT_USED_DISPLAY="${CONTEXT_USED}"
    fi

    if [ "$CONTEXT_LIMIT" -ge 1000 ]; then
        CONTEXT_LIMIT_K=$(echo "scale=0; $CONTEXT_LIMIT / 1000" | bc)
        CONTEXT_LIMIT_DISPLAY="${CONTEXT_LIMIT_K}k"
    else
        CONTEXT_LIMIT_DISPLAY="${CONTEXT_LIMIT}"
    fi

    # Smart warning levels based on percentage
    # Now that we include autocompact buffer, thresholds are higher
    if [ "$CONTEXT_PCT" -ge 95 ]; then
        # DANGER: Auto-compact imminent (at or past 95% = autocompact threshold)
        CONTEXT_PREFIX="!"
        CONTEXT_BG="$BG_RED"
        CONTEXT_FG="$FG_WHITE"
        CONTEXT_STYLE="$BOLD"
    elif [ "$CONTEXT_PCT" -ge 90 ]; then
        # WARNING: Approaching auto-compact zone (90-94%)
        CONTEXT_PREFIX="+"
        CONTEXT_BG="$BG_YELLOW"
        CONTEXT_FG="$FG_BLACK"
    else
        # NORMAL: All good (below 90%)
        CONTEXT_PREFIX=""
        CONTEXT_BG="$BG_GRAY"
        CONTEXT_FG="$FG_WHITE"
    fi

    CONTEXT_DISPLAY="${CONTEXT_USED_DISPLAY}/${CONTEXT_LIMIT_DISPLAY} ${CONTEXT_PREFIX}${CONTEXT_PCT}%"
fi

# Build statusline with 4 segments: Project → Git → Model → Context
OUTPUT=""

# Segment 1: Project name (Dark blue - foundational)
OUTPUT="${OUTPUT}${BG_DARKBLUE}${FG_WHITE} ${FOLDER_NAME} ${RESET}"
LAST_BG="DARKBLUE"
LAST_FG="DARKBLUE"

# Segment 2: Git (Green if clean, Red if dirty)
if [ -n "$GIT_BRANCH" ]; then
    OUTPUT="${OUTPUT}${FG_DARKBLUE}${GIT_BG}${SEP}${GIT_BG}${FG_WHITE} ${GIT_BRANCH} ${GIT_STATUS} ${RESET}"
    if [ "$GIT_STATUS" = "●" ]; then
        LAST_FG_COLOR="$FG_RED"
    else
        LAST_FG_COLOR="$FG_GREEN"
    fi
else
    LAST_FG_COLOR="$FG_DARKBLUE"
fi

# Segment 3: Model (Purple - capability indicator)
OUTPUT="${OUTPUT}${LAST_FG_COLOR}${BG_PURPLE}${SEP}${BG_PURPLE}${FG_WHITE} ${MODEL_DISPLAY} ${RESET}"

# Segment 4: Context (Dynamic color based on threshold - CRITICAL)
if [ -n "$CONTEXT_DISPLAY" ]; then
    OUTPUT="${OUTPUT}${FG_PURPLE}${CONTEXT_BG}${SEP}${CONTEXT_BG}${CONTEXT_FG}${CONTEXT_STYLE} ${CONTEXT_DISPLAY} ${RESET}"

    # Final separator color matches context background
    if [ "$CONTEXT_PCT" -ge 95 ]; then
        OUTPUT="${OUTPUT}${FG_RED}${SEP}"
    elif [ "$CONTEXT_PCT" -ge 90 ]; then
        OUTPUT="${OUTPUT}${FG_YELLOW}${SEP}"
    else
        OUTPUT="${OUTPUT}${FG_GRAY}${SEP}"
    fi
else
    OUTPUT="${OUTPUT}${FG_PURPLE}${SEP}"
fi

echo -e "$OUTPUT"

#!/usr/bin/env bash

# Copyright 2018 Google LLC
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
# =============================================================================


# Switch between different versions of deeplearn.js dependency.
#
# The script automatically modifies ./package.json
#
# Usage examples:
#
# 1. To depend on the HEAD of the public GitHub repo of deeplearn.js:
#   ./scripts/switch-deeplearn-version.sh --github
#
# 2. To depend on a given branch or tags  of the public GitHub repo of
#    deeplearn.js:
#   ./scripts/switch-deeplearn-version.sh --github --branch tags/v0.5.0
#
# 3. To depend on deeplearn.js built from a local repo, with any local
#    edits incorporated:
#   ./scripts/switch-deeplearn-version.sh --local_path "${HOME}/my-dljs"

set -e

ORIGIN_DIR="$(pwd)"

GITHUB=0
GIT_BRANCH=""
LOCAL_PATH=""

DEFAULT_TMP_REPO_DIR="/tmp/dljs-github-clean"

while [[ ! -z "$1" ]]; do
  if [[ "$1" == "--github" ]]; then
    GITHUB=1
    shift 1
  elif [[ "$1" == "--branch" ]]; then
    GIT_BRANCH="$2"
    shift 2
  elif [[ "$1" == "--local_path" ]]; then
    LOCAL_PATH="$2"
    if [[ -z "${LOCAL_PATH}" ]]; then
      echo "ERROR: Unspecified local path"
      exit 1
    fi
    shift 2
  else
    echo "ERROR: Unrecognized argument: $1"
    exit 1
  fi
done

# Do sanity checks on flags.
if [[ "${GITHUB}" == 1 ]] && [[ ! -z "${LOCAL_PATH}" ]]; then
  echo "ERROR: --github and --local_path are mutually exclusive."
  exit 1
fi

if [[ ! -z "${GIT_BRANCH}" ]] && [[ "${GITHUB}" == 0 ]]; then
  echo "ERROR: --branch flag can only be used with the --github flag."
  exit 1
fi

# Check yarn is on path.
if [[ -z "$(which yarn)" ]]; then
  echo "ERROR: switch-deeplearn-version.sh relies on yarn." \
    "But yarn is not found on path." \
    "See https://yarnpkg.com/lang/en/docs/install/"
  exit 1
fi

if [[ ${GITHUB} == 1 ]]; then
  REPO_DIR="${DEFAULT_TMP_REPO_DIR}"

  if [[ ! -d "${REPO_DIR}/deeplearnjs" ]]; then
    echo "Cloning deeplearn.js git repo to: ${REPO_DIR}"
    echo
    mkdir -p "${REPO_DIR}"
    cd "${REPO_DIR}"
    git clone https://github.com/PAIR-code/deeplearnjs.git
  fi
  cd "${REPO_DIR}/deeplearnjs"

  if [[ ! -z "${GIT_BRANCH}" ]]; then
    git checkout "${GIT_BRANCH}"
  fi
  git pull
elif [[ ! -z "${LOCAL_PATH}" ]]; then
  cd "${LOCAL_PATH}"
else
  echo "Must specify either --github or --local_path <LOCAL_PATH>"
  exit 1
fi

# Call yarn link / prep / build in the deeplearn source folder.
# In case another deeplearn repo has been registered.
yarn unlink || echo "No deeplearn is registered with yarn link."
yarn link
yarn prep
yarn build

# cd back to where we started and call yarn link deeplearn.
cd "${ORIGIN_DIR}"
rm -rf node_modules/deeplearn
yarn link deeplearn

# Call yarn link deeplearn for the demos/ directory.
cd "${ORIGIN_DIR}/demos"
rm -rf node_modules/deeplearn
yarn link deeplearn

echo "Linking to custom deeplearn source is done."
echo
echo "To switch back to the default deeplearn version, do:"
echo "  yarn unlink deeplearn && yarn"

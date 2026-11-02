#!/usr/bin/env bash
# Prepara una PR para el benchmark: un repo limpio con solo el head de la PR y su
# base, sin historia posterior (ni el commit que luego arregló el bug), y un
# worktree por ejecución.
#
#   prepare.sh repo <clon-local> <owner/repo> <pr> [sha-del-head]
#   prepare.sh runs <pr> <nombre-run>...
#
# BENCH (por defecto ./bench) es el directorio de trabajo: repos/ y runs/.
set -euo pipefail

BENCH=${BENCH:-./bench}

prepare_repo() {
  local clone=$1 slug=$2 pr=$3 head=${4:-}
  local json base_ref merge_commit tip base out
  json=$(gh pr view "$pr" --repo "$slug" --json baseRefName,headRefOid,mergeCommit)
  base_ref=$(jq -r .baseRefName <<<"$json")
  merge_commit=$(jq -r '.mergeCommit.oid // empty' <<<"$json")
  head=${head:-$(jq -r .headRefOid <<<"$json")}

  git -C "$clone" fetch -q origin "pull/$pr/head" "$head"
  if [[ -n $merge_commit ]]; then
    # PR mergeada: la rama base ya contiene la PR; se parte del commit previo al merge.
    git -C "$clone" fetch -q origin "$merge_commit"
    tip=$(git -C "$clone" rev-parse "$merge_commit^1")
  else
    git -C "$clone" fetch -q origin "$base_ref"
    tip=$(git -C "$clone" rev-parse FETCH_HEAD)
  fi
  base=$(git -C "$clone" merge-base "$head" "$tip")

  # Refs temporales en el clon: git solo deja traer por ref desde un repo local.
  git -C "$clone" update-ref "refs/bench/head-$pr" "$head"
  git -C "$clone" update-ref "refs/bench/base-$pr" "$base"
  out="$BENCH/repos/pr-$pr"
  rm -rf "$out"
  git init -q "$out"
  git -C "$out" fetch -q --update-shallow "$clone" \
    "refs/bench/head-$pr:refs/heads/pr-head" \
    "refs/bench/base-$pr:refs/remotes/origin/$base_ref"
  git -C "$clone" update-ref -d "refs/bench/head-$pr"
  git -C "$clone" update-ref -d "refs/bench/base-$pr"

  # Remoto real para que `gh` resuelva el repo, sin fetch ni push.
  git -C "$out" remote add origin "https://github.com/$slug.git"
  git -C "$out" config remote.origin.fetch '+refs/heads/__none__:refs/remotes/origin/__none__'
  git -C "$out" config remote.origin.pushurl no-push
  git -C "$out" symbolic-ref HEAD refs/heads/pr-head

  echo "pr=$pr base=origin/$base_ref ($(git -C "$out" rev-parse --short "origin/$base_ref")) head=$(git -C "$out" rev-parse --short pr-head)"
  git -C "$out" diff --shortstat "origin/$base_ref...pr-head"
}

prepare_runs() {
  local pr=$1 name
  shift
  for name in "$@"; do
    mkdir -p "$BENCH/runs/$name"
    git -C "$BENCH/repos/pr-$pr" worktree add -q --detach "$BENCH/runs/$name/wt" pr-head
    echo "$BENCH/runs/$name"
  done
}

case ${1:-} in
  repo) shift; prepare_repo "$@" ;;
  runs) shift; prepare_runs "$@" ;;
  *) sed -n '2,9p' "$0" >&2; exit 2 ;;
esac

#!/usr/bin/env bash
# Pide review al bot, espera a que su run termine e imprime la review nueva:
# estado, cuerpo y comentarios inline con su id (para responder en el hilo).
# REVIEW_BOT y REVIEW_WORKFLOW cambian el bot y el workflow que lanza su review.
set -euo pipefail

pr=${1:?uso: review.sh <PR>}
bot=${REVIEW_BOT:-isitech-bot}
workflow=${REVIEW_WORKFLOW:-claude-review.yml}
repo=$(gh repo view --json nameWithOwner -q .nameWithOwner)
read -r branch draft < <(gh pr view "$pr" --json headRefName,isDraft -q '"\(.headRefName) \(.isDraft)"')

# En draft el bot publica COMMENT y nunca aprueba: el bucle no terminaria.
if [ "$draft" = true ]; then
  echo "La PR #$pr es draft: pasala a lista (gh pr ready $pr) antes de pedir review." >&2
  exit 2
fi

# Ids previos en vez de fechas: el reloj local no interviene.
last_run=$(gh run list --workflow "$workflow" --branch "$branch" -L 1 --json databaseId -q '.[0].databaseId // 0')
last_review=$(gh api "repos/$repo/pulls/$pr/reviews" --paginate \
  -q ".[] | select(.user.login == \"$bot\") | .id" | tail -n 1)
last_review=${last_review:-0}

# Sirve tambien para volver a pedirla: dispara otro review_requested.
gh api -X POST "repos/$repo/pulls/$pr/requested_reviewers" -f "reviewers[]=$bot" >/dev/null

run=
for _ in $(seq 1 60); do
  run=$(gh run list --workflow "$workflow" --branch "$branch" -L 1 --json databaseId \
    -q ".[] | select(.databaseId > $last_run) | .databaseId")
  [ -n "$run" ] && break
  sleep 5
done
if [ -z "$run" ]; then
  echo "No ha arrancado ningun run de $workflow en 5 min." >&2
  exit 1
fi

if ! gh run watch "$run" --exit-status >/dev/null 2>&1; then
  echo "El run $run de $workflow ha fallado sin review. Detalle: gh run view $run --log-failed" >&2
  exit 1
fi

review=$(gh api "repos/$repo/pulls/$pr/reviews" --paginate \
  -q ".[] | select(.user.login == \"$bot\" and .id > $last_review) | {id, state, body}" | tail -n 1)
if [ -z "$review" ]; then
  echo "El run $run termino en verde pero no hay review nueva de $bot." >&2
  exit 1
fi

id=$(jq -r .id <<<"$review")
echo "ESTADO: $(jq -r .state <<<"$review")"
echo
jq -r .body <<<"$review"
echo
echo "COMENTARIOS INLINE:"
# reviews/{id}/comments no trae la linea: se filtra la lista de la PR.
gh api "repos/$repo/pulls/$pr/comments" --paginate \
  -q ".[] | select(.pull_request_review_id == $id) | \"\n[\(.id)] \(.path):\(.line // .original_line)\n\(.body)\""

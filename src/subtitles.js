export function formatSrtTimestamp(seconds) {
  const ms = Math.max(0, Math.round(seconds * 1000));
  const hours = Math.floor(ms / 3600000);
  const minutes = Math.floor((ms % 3600000) / 60000);
  const secs = Math.floor((ms % 60000) / 1000);
  const millis = ms % 1000;
  return String(hours).padStart(2, "0") + ":" + String(minutes).padStart(2, "0") + ":" +
    String(secs).padStart(2, "0") + "," + String(millis).padStart(3, "0");
}

export function buildSrt(scenes) {
  let cursor = 0;
  return scenes.map((scene, index) => {
    const start = cursor;
    cursor += Math.max(1, Number(scene.duration) || 1);
    return (index + 1) + "\n" + formatSrtTimestamp(start) + " --> " +
      formatSrtTimestamp(cursor) + "\n" + String(scene.narration ?? "").trim();
  }).join("\n\n") + (scenes.length ? "\n" : "");
}

export function wrapCaption(text, maxChars = 58, maxLines = 2) {
  const words = String(text ?? "").trim().split(/\s+/).filter(Boolean);
  const lines = [];
  let line = "";
  for (const word of words) {
    const next = line ? line + " " + word : word;
    if (next.length > maxChars && line) {
      lines.push(line);
      line = word;
    } else line = next;
  }
  if (line) lines.push(line);
  if (lines.length > maxLines) {
    const visible = lines.slice(0, maxLines);
    const last = visible[maxLines - 1];
    visible[maxLines - 1] = last.length > maxChars - 1
      ? last.slice(0, maxChars - 1).trimEnd() + "…"
      : last + "…";
    return visible;
  }
  return lines;
}

// Registered only when a Wiser hub enables "Pre-cache resource images".
// Identical URLs let every card reuse the browser's normal HTTP image cache.
const version = new URL(import.meta.url).searchParams.get("v");
fetch(`/wiser/images/manifest.json?v=${encodeURIComponent(version || "")}`)
  .then((response) => {
    if (!response.ok) throw new Error("Unable to load Wiser image catalogue");
    return response.json();
  })
  .then((images) => {
    for (const url of new Set(Object.values(images))) {
      const image = new Image();
      image.src = url;
    }
  })
  .catch((error) => console.debug("Wiser image pre-cache unavailable", error));

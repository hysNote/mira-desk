// One complete atmosphere per style, shared by dropdown, bell and direct URLs.
export const STYLE_WINDOWS=Object.freeze({
 original:'sunset',comic:'sunset',noir:'storm',pop:'rainbow',anime:'ocean',
 watercolor:'snow',punk:'storm',neon:'ocean',sketch:'sunset',pixel:'rainbow',void:'snow'
});
export const windowForStyle=id=>STYLE_WINDOWS[id]||STYLE_WINDOWS.original;

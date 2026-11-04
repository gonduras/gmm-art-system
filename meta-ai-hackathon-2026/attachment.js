/* MeshAttachment — beak-to-tail adapter (Three r128, UMD).
 * Anchors live on actual (possibly transformed child) meshes, not scene roots.
 * solve() moves fishRoot translation only, in parent space, preserving all
 * rotations/scales/child transforms. No quaternion decomposition is used:
 * world delta is mapped through the inverse of the parent linear (3x3) part.
 * NOTE: anchors on deforming/skinned geometry require the caller to keep
 * beakLocal/tailLocal updated from actual vertex coordinates or artist
 * attachment landmarks. A stale vertex location is NOT fixed by matrices.
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.MeshAttachment = factory();
}(typeof self !== "undefined" ? self : this, function () {
  var VERSION = 1;
  function isObj(o) {
    return !!o && o.isObject3D === true && typeof o.updateWorldMatrix === "function" && o.matrixWorld;
  }
  function isLocal(v) {
    return Array.isArray(v) && v.length === 3 &&
      Number.isFinite(v[0]) && Number.isFinite(v[1]) && Number.isFinite(v[2]);
  }
  function isDescendant(obj, rootObj) {
    var n = obj;
    while (n) { if (n === rootObj) return true; n = n.parent; }
    return false;
  }
  function v3(THREE, a) { return new THREE.Vector3(a[0], a[1], a[2]); }
  function finiteV(v) {
    return Number.isFinite(v.x) && Number.isFinite(v.y) && Number.isFinite(v.z);
  }
  function createAttachment(THREE, opts) {
    if (!THREE || !THREE.Vector3) throw new Error("THREE required");
    opts = opts || {};
    var birdAnchorObject = opts.birdAnchorObject, fishAnchorObject = opts.fishAnchorObject,
        fishRoot = opts.fishRoot, beakLocal = opts.beakLocal, tailLocal = opts.tailLocal;
    if (!isObj(birdAnchorObject)) throw new Error("bad birdAnchorObject");
    if (!isObj(fishAnchorObject)) throw new Error("bad fishAnchorObject");
    if (!isObj(fishRoot)) throw new Error("bad fishRoot");
    if (!isDescendant(fishAnchorObject, fishRoot)) throw new Error("fishAnchorObject must be fishRoot or its descendant");
    if (birdAnchorObject === fishRoot || isDescendant(birdAnchorObject, fishRoot))
      throw new Error("birdAnchorObject must not descend from fishRoot");
    if (!isLocal(beakLocal)) throw new Error("bad beakLocal");
    if (!isLocal(tailLocal)) throw new Error("bad tailLocal");
    var beak = beakLocal.slice(), tail = tailLocal.slice();
    var origPos = fishRoot.position.clone();
    function worldOf(obj, local) {
      obj.updateWorldMatrix(true, false);
      var v = v3(THREE, local).applyMatrix4(obj.matrixWorld);
      return v;
    }
    function solve() {
      if (!isLocal(beak) || !isLocal(tail)) throw new Error("nonfinite anchor");
      var bw = worldOf(birdAnchorObject, beak);
      var tw = worldOf(fishAnchorObject, tail);
      if (!finiteV(bw) || !finiteV(tw)) throw new Error("nonfinite world anchor");
      var dx = bw.x - tw.x, dy = bw.y - tw.y, dz = bw.z - tw.z;
      if (!Number.isFinite(dx) || !Number.isFinite(dy) || !Number.isFinite(dz))
        throw new Error("nonfinite delta");
      var parent = fishRoot.parent;
      var lx = dx, ly = dy, lz = dz;
      if (parent) {
        parent.updateWorldMatrix(true, false);
        var determinant = parent.matrixWorld.determinant();
        if (!parent.matrixWorld.elements.every(Number.isFinite) || !Number.isFinite(determinant) || Math.abs(determinant) < 1e-20)
          throw new Error("singular parent");
        // Codex: use tested Three.js inversion; map a delta without translation or normalization.
        var inv = parent.matrixWorld.clone().invert().elements;
        lx = inv[0] * dx + inv[4] * dy + inv[8] * dz;
        ly = inv[1] * dx + inv[5] * dy + inv[9] * dz;
        lz = inv[2] * dx + inv[6] * dy + inv[10] * dz;
        if (!Number.isFinite(lx) || !Number.isFinite(ly) || !Number.isFinite(lz))
          throw new Error("nonfinite local delta");
      }
      var px = fishRoot.position.x, py = fishRoot.position.y, pz = fishRoot.position.z;
      if (!Number.isFinite(px) || !Number.isFinite(py) || !Number.isFinite(pz))
        throw new Error("nonfinite root position");
      if (![px + lx, py + ly, pz + lz].every(Number.isFinite))
        throw new Error("nonfinite solved position");
      fishRoot.position.set(px + lx, py + ly, pz + lz);
      fishRoot.updateMatrix();
      return getError();
    }
    function getError() {
      var bw = worldOf(birdAnchorObject, beak);
      var tw = worldOf(fishAnchorObject, tail);
      return bw.distanceTo(tw);
    }
    function setAnchors(nb, nt) {
      var a = nb, b = nt; // allow setAnchors({beakLocal,tailLocal})
      if (nb && !Array.isArray(nb) && typeof nb === "object") {
        a = nb.beakLocal !== undefined ? nb.beakLocal : beak;
        b = nb.tailLocal !== undefined ? nb.tailLocal : tail;
      }
      if (a === undefined) a = beak;
      if (b === undefined) b = tail;
      if (!isLocal(a)) throw new Error("bad beakLocal");
      if (!isLocal(b)) throw new Error("bad tailLocal");
      beak = a.slice(); tail = b.slice(); // atomic: validated first
    }
    function snapshot() {
      return { version: VERSION, anchors: { beakLocal: beak.slice(), tailLocal: tail.slice() },
        originalFishRootPosition: [origPos.x, origPos.y, origPos.z] };
    }
    function restore(snap) {
      var before = snapshot();
      try {
        if (!snap || typeof snap !== "object") throw new Error("bad snapshot");
        if (snap.version !== VERSION) throw new Error("bad version");
        if (!snap.anchors || !isLocal(snap.anchors.beakLocal) || !isLocal(snap.anchors.tailLocal))
          throw new Error("bad anchors");
        if (!isLocal(snap.originalFishRootPosition)) throw new Error("bad originalFishRootPosition");
        beak = snap.anchors.beakLocal.slice();
        tail = snap.anchors.tailLocal.slice();
        origPos = v3(THREE, snap.originalFishRootPosition);
      } catch (e) { // atomic: identical state
        beak = before.anchors.beakLocal.slice(); tail = before.anchors.tailLocal.slice();
        origPos = v3(THREE, before.originalFishRootPosition);
        throw e;
      }
      // never touches scene; takes effect on solve()/reset()
    }
    function reset() { fishRoot.position.copy(origPos); fishRoot.updateMatrix(); }
    function getAnchors() { return { beakLocal: beak.slice(), tailLocal: tail.slice() }; }
    return { solve: solve, reset: reset, getError: getError, setAnchors: setAnchors,
      getAnchors: getAnchors, snapshot: snapshot, restore: restore };
  }
  return { createAttachment: createAttachment, VERSION: VERSION };
}));

<script setup>
/**
 * Premium cover slide layout with geometric ring decoration and gradient accents.
 */
</script>

<template>
  <div class="cover-layout">
    <!-- Geometric ring decorations -->
    <div class="cover-ring cover-ring-1" />
    <div class="cover-ring cover-ring-2" />
    <div class="cover-ring cover-ring-3" />

    <div class="cover-content">
      <slot />
    </div>

    <div class="cover-footer">
      <div class="cover-line" />
    </div>
  </div>
</template>

<style scoped>
.cover-layout {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background: #1A1A2E;
  position: relative;
  overflow: hidden;
  padding: 60px;
}

/* Geometric ring constellation — concentric outlines, not blurry blobs */
.cover-ring {
  position: absolute;
  border-radius: 50%;
  pointer-events: none;
}

.cover-ring-1 {
  top: -80px;
  right: -80px;
  width: 360px;
  height: 360px;
  border: 1.5px solid rgba(232, 93, 38, 0.18);
}

.cover-ring-2 {
  top: -20px;
  right: -20px;
  width: 240px;
  height: 240px;
  border: 1px solid rgba(139, 92, 246, 0.14);
}

.cover-ring-3 {
  bottom: -120px;
  left: -120px;
  width: 320px;
  height: 320px;
  border: 1px solid rgba(74, 144, 217, 0.12);
}

.cover-content {
  text-align: center;
  z-index: 1;
  max-width: 80%;
}

.cover-content :deep(h1) {
  font-family: 'DM Sans', sans-serif;
  font-size: 3.2em;
  font-weight: 700;
  letter-spacing: -0.03em;
  line-height: 1.1;
  background: linear-gradient(135deg, #FFFFFF 0%, #EAEAF0 50%, #C4B5FD 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 16px;
}

.cover-content :deep(h2) {
  font-family: 'DM Sans', sans-serif;
  font-size: 1.3em;
  font-weight: 300;
  color: #FF7A45;
  letter-spacing: 0.01em;
  margin-bottom: 8px;
}

.cover-content :deep(p) {
  font-size: 1.15em;
  color: #9B9BB4;
  line-height: 1.6;
}

.cover-footer {
  position: absolute;
  bottom: 40px;
}

.cover-line {
  width: 48px;
  height: 3px;
  background: linear-gradient(90deg, #E85D26, #F5A623, #8B5CF6);
  border-radius: 2px;
}
</style>

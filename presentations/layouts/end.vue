<script setup>
/**
 * Closing slide layout — minimal, no heavy decoration.
 * Used for Q&A, contact info, and final takeaway slides.
 */
</script>

<template>
  <div class="end-layout">
    <div class="end-line-top" />
    <div class="end-content">
      <slot />
    </div>
    <div class="end-line-bottom" />
  </div>
</template>

<style scoped>
.end-layout {
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

.end-line-top {
  position: absolute;
  top: 48px;
  left: 50%;
  transform: translateX(-50%);
  width: 60px;
  height: 2px;
  background: linear-gradient(90deg, #E85D26, #F5A623);
  border-radius: 1px;
}

.end-content {
  text-align: center;
  z-index: 1;
  max-width: 75%;
}

.end-content :deep(h1) {
  font-family: 'DM Sans', sans-serif;
  font-size: 2.4em;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: #EAEAF0;
  margin-bottom: 16px;
}

.end-content :deep(h2) {
  font-family: 'DM Sans', sans-serif;
  font-size: 1.2em;
  font-weight: 400;
  color: #9B9BB4;
  margin-bottom: 8px;
}

.end-content :deep(p) {
  font-size: 1em;
  color: #6B6B82;
  line-height: 1.6;
}

.end-line-bottom {
  position: absolute;
  bottom: 40px;
  left: 50%;
  transform: translateX(-50%);
  width: 40px;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.15), transparent);
  border-radius: 1px;
}
</style>

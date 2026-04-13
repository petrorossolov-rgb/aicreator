<script setup>
/**
 * Section break layout — used between major parts of a presentation.
 * Features an enhanced accent bar and subtle geometric detail.
 */
</script>

<template>
  <div class="section-layout">
    <div class="section-accent" />
    <div class="section-glow" />
    <div class="section-content">
      <slot />
    </div>
    <div class="section-bottom-line" />
  </div>
</template>

<style scoped>
.section-layout {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #1A1A2E;
  position: relative;
  overflow: hidden;
}

.section-accent {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 8px;
  background: linear-gradient(180deg, #E85D26, #F5A623, #8B5CF6);
}

/* Subtle radial glow in the top-right corner for visual depth */
.section-glow {
  position: absolute;
  top: -150px;
  right: -150px;
  width: 350px;
  height: 350px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(139, 92, 246, 0.06) 0%, transparent 70%);
  pointer-events: none;
}

.section-content {
  text-align: center;
  padding: 60px;
}

.section-content :deep(h1) {
  font-family: 'DM Sans', sans-serif;
  font-size: 2.8em;
  font-weight: 700;
  color: #EAEAF0;
  letter-spacing: -0.02em;
}

.section-content :deep(p) {
  font-size: 1.1em;
  color: #9B9BB4;
  margin-top: 12px;
}

.section-bottom-line {
  position: absolute;
  bottom: 48px;
  left: 50%;
  transform: translateX(-50%);
  width: 40px;
  height: 2px;
  background: linear-gradient(90deg, #E85D26, #F5A623);
  border-radius: 1px;
}
</style>

<script setup>
/**
 * Metrics layout — title at top, content area optimized for KpiCard grids.
 */
</script>

<template>
  <div class="metrics-layout">
    <div class="metrics-content">
      <slot />
    </div>
  </div>
</template>

<style scoped>
.metrics-layout {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #1A1A2E;
  padding: 48px 60px;
}

.metrics-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
}

.metrics-content :deep(h1) {
  font-family: 'DM Sans', sans-serif;
  font-weight: 700;
  font-size: 1.8em;
  color: #EAEAF0;
  margin-bottom: 32px;
  letter-spacing: -0.02em;
}

/* Auto-grid for KPI cards when placed in a div.grid */
.metrics-content :deep(.grid) {
  display: grid;
  gap: 20px;
}
.metrics-content :deep(.grid-2) { grid-template-columns: repeat(2, 1fr); }
.metrics-content :deep(.grid-3) { grid-template-columns: repeat(3, 1fr); }
.metrics-content :deep(.grid-4) { grid-template-columns: repeat(4, 1fr); }
</style>

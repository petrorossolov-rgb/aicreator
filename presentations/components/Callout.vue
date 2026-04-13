<script setup>
/**
 * Callout/alert component for highlighting important information.
 * More structured than QuoteBlock — for warnings, insights, and key points.
 *
 * Usage:
 *   <Callout type="warning" title="Breaking Change">API v1 deprecated in Q3</Callout>
 *   <Callout type="insight">Key observation about the data</Callout>
 */
defineProps({
  type: {
    type: String,
    default: 'info',
    validator: (v) => ['info', 'warning', 'success', 'insight'].includes(v),
  },
  title: { type: String, default: '' },
})

const typeMap = {
  info: { accent: '#4A90D9', bg: 'rgba(74, 144, 217, 0.08)', border: 'rgba(74, 144, 217, 0.2)', icon: 'ℹ' },
  warning: { accent: '#F5A623', bg: 'rgba(245, 166, 35, 0.08)', border: 'rgba(245, 166, 35, 0.2)', icon: '⚠' },
  success: { accent: '#34C77B', bg: 'rgba(52, 199, 123, 0.08)', border: 'rgba(52, 199, 123, 0.2)', icon: '✓' },
  insight: { accent: '#8B5CF6', bg: 'rgba(139, 92, 246, 0.08)', border: 'rgba(139, 92, 246, 0.2)', icon: '✦' },
}
</script>

<template>
  <div
    class="callout"
    :style="{
      background: typeMap[type].bg,
      borderColor: typeMap[type].border,
      borderLeftColor: typeMap[type].accent,
    }"
  >
    <div class="callout-icon" :style="{ color: typeMap[type].accent }">
      {{ typeMap[type].icon }}
    </div>
    <div class="callout-body">
      <div v-if="title" class="callout-title" :style="{ color: typeMap[type].accent }">
        {{ title }}
      </div>
      <div class="callout-text"><slot /></div>
    </div>
  </div>
</template>

<style scoped>
.callout {
  display: flex;
  gap: 16px;
  align-items: flex-start;
  border: 1px solid;
  border-left-width: 3px;
  border-radius: 0 10px 10px 0;
  padding: 18px 22px;
}
.callout-icon {
  font-size: 1.2em;
  line-height: 1;
  flex-shrink: 0;
  margin-top: 2px;
}
.callout-body {
  flex: 1;
}
.callout-title {
  font-family: 'DM Sans', sans-serif;
  font-weight: 600;
  font-size: 0.95em;
  margin-bottom: 4px;
}
.callout-text {
  font-size: 0.9em;
  color: #EAEAF0;
  line-height: 1.5;
}
</style>

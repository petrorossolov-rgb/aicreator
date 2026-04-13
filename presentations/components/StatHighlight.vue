<script setup>
/**
 * Hero stat component — a single massive number dominating the slide.
 * Use when one metric is the entire story of the slide.
 *
 * Usage:
 *   <StatHighlight value="3x" label="Faster deployment" sublabel="compared to manual process" color="brand" />
 */
defineProps({
  value: { type: String, required: true },
  label: { type: String, required: true },
  sublabel: { type: String, default: '' },
  color: { type: String, default: 'brand' },
})

const colorMap = {
  brand: { value: '#FF7A45', glow: 'rgba(232, 93, 38, 0.08)' },
  blue: { value: '#4A90D9', glow: 'rgba(74, 144, 217, 0.08)' },
  green: { value: '#34C77B', glow: 'rgba(52, 199, 123, 0.08)' },
  amber: { value: '#F5A623', glow: 'rgba(245, 166, 35, 0.08)' },
  purple: { value: '#8B5CF6', glow: 'rgba(139, 92, 246, 0.08)' },
}
</script>

<template>
  <div class="stat-highlight">
    <div
      class="stat-glow"
      :style="{ background: `radial-gradient(circle, ${colorMap[color]?.glow || colorMap.brand.glow} 0%, transparent 70%)` }"
    />
    <div
      class="stat-value"
      :style="{ color: colorMap[color]?.value || colorMap.brand.value }"
    >
      {{ value }}
    </div>
    <div class="stat-label">{{ label }}</div>
    <div v-if="sublabel" class="stat-sublabel">{{ sublabel }}</div>
  </div>
</template>

<style scoped>
.stat-highlight {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  position: relative;
  padding: 40px 20px;
}
.stat-glow {
  position: absolute;
  width: 400px;
  height: 400px;
  border-radius: 50%;
  pointer-events: none;
}
.stat-value {
  font-family: 'DM Sans', sans-serif;
  font-size: 5.5em;
  font-weight: 700;
  line-height: 1;
  letter-spacing: -0.04em;
  position: relative;
  z-index: 1;
}
.stat-label {
  font-family: 'DM Sans', sans-serif;
  font-size: 1.3em;
  font-weight: 500;
  color: #EAEAF0;
  margin-top: 16px;
  letter-spacing: -0.01em;
  position: relative;
  z-index: 1;
}
.stat-sublabel {
  font-size: 0.9em;
  color: #6B6B82;
  margin-top: 8px;
  position: relative;
  z-index: 1;
}
</style>

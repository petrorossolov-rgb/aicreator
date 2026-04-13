<script setup>
/**
 * KPI metric card with icon, value, label, and optional trend indicator.
 *
 * Usage:
 *   <KpiCard value="94%" label="Uptime" trend="+2.1%" color="green" icon="carbon:activity" />
 *   <KpiCard value="1.2s" label="Avg Response" trend="-340ms" positive color="blue" />
 */
const props = defineProps({
  value: { type: String, required: true },
  label: { type: String, required: true },
  trend: { type: String, default: '' },
  positive: { type: Boolean, default: undefined },
  color: { type: String, default: 'brand' },
  icon: { type: String, default: '' },
  subtitle: { type: String, default: '' },
})

const colorMap = {
  brand: { bg: 'rgba(232, 93, 38, 0.1)', border: 'rgba(232, 93, 38, 0.3)', text: '#FF7A45' },
  blue: { bg: 'rgba(74, 144, 217, 0.1)', border: 'rgba(74, 144, 217, 0.3)', text: '#4A90D9' },
  green: { bg: 'rgba(52, 199, 123, 0.1)', border: 'rgba(52, 199, 123, 0.3)', text: '#34C77B' },
  amber: { bg: 'rgba(245, 166, 35, 0.1)', border: 'rgba(245, 166, 35, 0.3)', text: '#F5A623' },
  purple: { bg: 'rgba(139, 92, 246, 0.1)', border: 'rgba(139, 92, 246, 0.3)', text: '#8B5CF6' },
  red: { bg: 'rgba(231, 76, 94, 0.1)', border: 'rgba(231, 76, 94, 0.3)', text: '#E74C5E' },
}

const c = colorMap[props.color] || colorMap.brand

const isPositive = props.positive !== undefined
  ? props.positive
  : props.trend.startsWith('+') || props.trend.startsWith('-') ? props.trend.startsWith('+') : null
</script>

<template>
  <div class="kpi-card" :style="{ background: c.bg, borderColor: c.border }">
    <div v-if="icon" class="kpi-icon">
      <div class="icon-circle" :style="{ background: c.border }">
        <span class="icon-char">{{ icon }}</span>
      </div>
    </div>
    <div class="kpi-value" :style="{ color: c.text }">{{ value }}</div>
    <div class="kpi-label">{{ label }}</div>
    <div v-if="subtitle" class="kpi-subtitle">{{ subtitle }}</div>
    <div v-if="trend" class="kpi-trend" :class="{ positive: isPositive === true, negative: isPositive === false }">
      <span v-if="isPositive === true">↑</span>
      <span v-else-if="isPositive === false">↓</span>
      {{ trend }}
    </div>
  </div>
</template>

<style scoped>
.kpi-card {
  border: 1px solid;
  border-radius: 12px;
  padding: 24px;
  text-align: center;
  transition: all 0.3s ease;
}
.kpi-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
}
.kpi-icon {
  margin-bottom: 12px;
}
.icon-circle {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
.icon-char {
  font-size: 1.2em;
  line-height: 1;
}
.kpi-value {
  font-family: 'DM Sans', sans-serif;
  font-size: 2.4em;
  font-weight: 700;
  line-height: 1.1;
  letter-spacing: -0.02em;
}
.kpi-label {
  font-size: 0.85em;
  color: #9B9BB4;
  margin-top: 6px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-weight: 500;
}
.kpi-subtitle {
  font-size: 0.8em;
  color: #6B6B82;
  margin-top: 4px;
}
.kpi-trend {
  font-size: 0.8em;
  font-weight: 600;
  margin-top: 10px;
  padding: 3px 10px;
  border-radius: 999px;
  display: inline-block;
}
.kpi-trend.positive {
  background: rgba(52, 199, 123, 0.12);
  color: #34C77B;
}
.kpi-trend.negative {
  background: rgba(231, 76, 94, 0.12);
  color: #E74C5E;
}
</style>

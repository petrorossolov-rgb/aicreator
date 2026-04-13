<script setup>
/**
 * Feature card with icon, title, and description.
 *
 * Usage:
 *   <FeatureCard title="Real-time Sync" color="blue">
 *     Instant data synchronization across all devices
 *   </FeatureCard>
 */
defineProps({
  title: { type: String, required: true },
  color: { type: String, default: 'brand' },
  icon: { type: String, default: '' },
})

const colorMap = {
  brand: { accent: '#E85D26', bg: 'rgba(232, 93, 38, 0.08)', border: 'rgba(232, 93, 38, 0.2)' },
  blue: { accent: '#4A90D9', bg: 'rgba(74, 144, 217, 0.08)', border: 'rgba(74, 144, 217, 0.2)' },
  green: { accent: '#34C77B', bg: 'rgba(52, 199, 123, 0.08)', border: 'rgba(52, 199, 123, 0.2)' },
  amber: { accent: '#F5A623', bg: 'rgba(245, 166, 35, 0.08)', border: 'rgba(245, 166, 35, 0.2)' },
  purple: { accent: '#8B5CF6', bg: 'rgba(139, 92, 246, 0.08)', border: 'rgba(139, 92, 246, 0.2)' },
}
</script>

<template>
  <div
    class="feature-card"
    :style="{
      background: colorMap[color]?.bg || colorMap.brand.bg,
      borderColor: colorMap[color]?.border || colorMap.brand.border,
    }"
  >
    <div class="feature-accent" :style="{ background: colorMap[color]?.accent || colorMap.brand.accent }" />
    <div class="feature-content">
      <h4 class="feature-title" :style="{ color: colorMap[color]?.accent || colorMap.brand.accent }">
        {{ title }}
      </h4>
      <p class="feature-desc"><slot /></p>
    </div>
  </div>
</template>

<style scoped>
.feature-card {
  border: 1px solid;
  border-radius: 12px;
  padding: 20px 20px 20px 24px;
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
}
.feature-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.25);
}
.feature-accent {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
}
.feature-content {
  padding-left: 4px;
}
.feature-title {
  font-family: 'DM Sans', sans-serif;
  font-weight: 700;
  font-size: 1em;
  margin: 0 0 6px 0;
}
.feature-desc {
  font-size: 0.85em;
  color: #9B9BB4;
  margin: 0;
  line-height: 1.5;
}
</style>

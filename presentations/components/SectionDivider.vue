<script setup>
/**
 * Section divider slide content — large title with optional subtitle.
 * Use with layout: center for full-page section breaks.
 *
 * Usage:
 *   <SectionDivider title="Key Findings" subtitle="Based on Q4 2025 data" number="02" />
 */
defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: '' },
  number: { type: String, default: '' },
})
</script>

<template>
  <div class="section-divider">
    <div v-if="number" class="section-number">{{ number }}</div>
    <h1 class="section-title">{{ title }}</h1>
    <div class="section-line" />
    <p v-if="subtitle" class="section-subtitle">{{ subtitle }}</p>
  </div>
</template>

<style scoped>
.section-divider {
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.section-number {
  font-family: 'DM Sans', sans-serif;
  font-size: 4em;
  font-weight: 700;
  background: linear-gradient(135deg, #FF7A45, #F5A623);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1;
  margin-bottom: 12px;
  opacity: 0.7;
}
.section-title {
  font-family: 'DM Sans', sans-serif;
  font-size: 2.5em !important;
  font-weight: 700;
  color: #EAEAF0;
  letter-spacing: -0.02em;
  margin: 0;
}
.section-line {
  width: 60px;
  height: 3px;
  background: linear-gradient(90deg, #E85D26, #F5A623);
  border-radius: 2px;
  margin: 20px 0;
}
.section-subtitle {
  font-size: 1.1em;
  color: #9B9BB4;
  max-width: 500px;
}
</style>

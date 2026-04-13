<script setup>
/**
 * Horizontal numbered process steps — for sequential workflows.
 * Simpler than Timeline, better than a numbered list.
 *
 * Usage:
 *   <ProcessFlow :steps="[
 *     { title: 'Research', description: 'Analyze market and competitors' },
 *     { title: 'Plan', description: 'Define scope and architecture' },
 *     { title: 'Execute', description: 'Build incrementally with verification' },
 *   ]" />
 */
defineProps({
  steps: { type: Array, required: true },
  color: { type: String, default: 'brand' },
})

const colorMap = {
  brand: { num: '#E85D26', numBg: 'rgba(232, 93, 38, 0.15)', line: 'rgba(232, 93, 38, 0.3)' },
  blue: { num: '#4A90D9', numBg: 'rgba(74, 144, 217, 0.15)', line: 'rgba(74, 144, 217, 0.3)' },
  green: { num: '#34C77B', numBg: 'rgba(52, 199, 123, 0.15)', line: 'rgba(52, 199, 123, 0.3)' },
  purple: { num: '#8B5CF6', numBg: 'rgba(139, 92, 246, 0.15)', line: 'rgba(139, 92, 246, 0.3)' },
}
</script>

<template>
  <div class="process-flow">
    <div
      v-for="(step, i) in steps"
      :key="i"
      class="process-step"
    >
      <!-- Connector line -->
      <div
        v-if="i > 0"
        class="process-line"
        :style="{ background: colorMap[color]?.line || colorMap.brand.line }"
      />

      <!-- Number circle -->
      <div
        class="process-number"
        :style="{
          background: colorMap[color]?.numBg || colorMap.brand.numBg,
          color: colorMap[color]?.num || colorMap.brand.num,
        }"
      >
        {{ i + 1 }}
      </div>

      <!-- Text -->
      <div class="process-title">{{ step.title }}</div>
      <div v-if="step.description" class="process-desc">{{ step.description }}</div>
    </div>
  </div>
</template>

<style scoped>
.process-flow {
  display: flex;
  align-items: flex-start;
  padding: 20px 0;
}
.process-step {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  text-align: center;
}
.process-line {
  position: absolute;
  top: 24px;
  right: 50%;
  width: 100%;
  height: 2px;
  z-index: 0;
}
.process-number {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'DM Sans', sans-serif;
  font-size: 1.2em;
  font-weight: 700;
  position: relative;
  z-index: 1;
}
.process-title {
  font-family: 'DM Sans', sans-serif;
  font-weight: 600;
  font-size: 0.9em;
  color: #EAEAF0;
  margin-top: 14px;
}
.process-desc {
  font-size: 0.8em;
  color: #9B9BB4;
  margin-top: 6px;
  max-width: 150px;
  line-height: 1.4;
}
</style>

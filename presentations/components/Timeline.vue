<script setup>
/**
 * Horizontal timeline component for project phases.
 *
 * Usage:
 *   <Timeline :items="[
 *     { label: 'Research', date: 'Jan 2025', status: 'done' },
 *     { label: 'Development', date: 'Feb-Mar', status: 'active' },
 *     { label: 'Launch', date: 'Apr 2025', status: 'pending' },
 *   ]" />
 */
defineProps({
  items: {
    type: Array,
    required: true,
    // Each item: { label: string, date?: string, status: 'done' | 'active' | 'pending' }
  },
})

const statusStyles = {
  done: { bg: '#34C77B', ring: 'rgba(52, 199, 123, 0.25)', text: '#34C77B' },
  active: { bg: '#E85D26', ring: 'rgba(232, 93, 38, 0.25)', text: '#FF7A45' },
  pending: { bg: '#6B6B82', ring: 'rgba(107, 107, 130, 0.2)', text: '#9B9BB4' },
}
</script>

<template>
  <div class="timeline">
    <div class="timeline-track">
      <div
        v-for="(item, i) in items"
        :key="i"
        class="timeline-item"
        :style="{ flex: 1 }"
      >
        <!-- Connector line -->
        <div
          v-if="i > 0"
          class="timeline-line"
          :style="{ background: item.status === 'pending' ? '#2D2D4A' : statusStyles[item.status].bg }"
        />

        <!-- Node -->
        <div class="timeline-node">
          <div
            class="node-ring"
            :style="{ background: statusStyles[item.status].ring }"
          >
            <div
              class="node-dot"
              :style="{ background: statusStyles[item.status].bg }"
            >
              <span v-if="item.status === 'done'" class="node-check">✓</span>
              <span v-else-if="item.status === 'active'" class="node-pulse" />
            </div>
          </div>
        </div>

        <!-- Label -->
        <div class="timeline-label" :style="{ color: statusStyles[item.status].text }">
          {{ item.label }}
        </div>
        <div v-if="item.date" class="timeline-date">
          {{ item.date }}
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.timeline {
  padding: 20px 0;
}
.timeline-track {
  display: flex;
  align-items: flex-start;
  position: relative;
}
.timeline-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
}
.timeline-line {
  position: absolute;
  top: 20px;
  right: 50%;
  width: 100%;
  height: 2px;
  z-index: 0;
}
.timeline-node {
  position: relative;
  z-index: 1;
}
.node-ring {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}
.node-dot {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}
.node-check {
  color: white;
  font-size: 0.65em;
  font-weight: 700;
}
.node-pulse {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: white;
  animation: pulse 2s infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(0.8); }
}
.timeline-label {
  margin-top: 12px;
  font-family: 'DM Sans', sans-serif;
  font-weight: 600;
  font-size: 0.85em;
  text-align: center;
}
.timeline-date {
  margin-top: 4px;
  font-size: 0.75em;
  color: #6B6B82;
}
</style>

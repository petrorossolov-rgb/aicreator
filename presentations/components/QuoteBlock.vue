<script setup>
/**
 * Styled quote / insight block with accent bar and optional author.
 *
 * Usage:
 *   <QuoteBlock author="CTO, Acme Corp" color="brand">
 *     This solution reduced our deployment time by 80%
 *   </QuoteBlock>
 */
defineProps({
  author: { type: String, default: '' },
  color: { type: String, default: 'brand' },
})

const colorMap = {
  brand: '#E85D26',
  blue: '#4A90D9',
  green: '#34C77B',
  amber: '#F5A623',
  purple: '#8B5CF6',
}
</script>

<template>
  <div class="quote-block" :style="{ borderLeftColor: colorMap[color] || colorMap.brand }">
    <div class="quote-mark" :style="{ color: colorMap[color] || colorMap.brand }">"</div>
    <div class="quote-text"><slot /></div>
    <div v-if="author" class="quote-author">
      <span class="author-dash" :style="{ background: colorMap[color] || colorMap.brand }" />
      {{ author }}
    </div>
  </div>
</template>

<style scoped>
.quote-block {
  border-left: 3px solid;
  padding: 24px 28px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 0 12px 12px 0;
  position: relative;
}
.quote-mark {
  font-family: 'DM Sans', serif;
  font-size: 3em;
  line-height: 1;
  position: absolute;
  top: 8px;
  left: 16px;
  opacity: 0.3;
}
.quote-text {
  font-size: 1.15em;
  line-height: 1.6;
  color: #EAEAF0;
  font-style: italic;
  padding-left: 8px;
}
.quote-author {
  margin-top: 14px;
  font-size: 0.85em;
  color: #9B9BB4;
  display: flex;
  align-items: center;
  gap: 10px;
  padding-left: 8px;
}
.author-dash {
  width: 20px;
  height: 2px;
  border-radius: 1px;
}
</style>

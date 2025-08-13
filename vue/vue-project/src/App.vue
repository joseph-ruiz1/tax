<script setup>
import { ref, computed } from 'vue'

const count = ref(0)

function increment() {
  count.value++
}

const counting = computed(() => {
  return count.value > 1 ? 'positive' : 'negative'
})
</script>

<template>
  <button @click="increment">
    {{ count }}
  </button>

  <p>count?</p>
  <span>{{ counting }}</span>
</template>
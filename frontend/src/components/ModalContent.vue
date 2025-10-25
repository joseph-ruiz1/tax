<template>
  <div class="modal-overlay" @click="handleOverlayClick">
    <div class="modal-container" @click.stop>
      <!-- Header -->
      <div class="modal-header">
        <h2 class="modal-title">{{ title }}</h2>
        <button class="modal-close-btn" @click="$emit('close')" aria-label="Close modal">
          ×
        </button>
      </div>
      
      <!-- Body - This is where your custom content goes -->
      <div class="modal-body">
        <slot>
          <!-- Default content if no slot provided -->
          <p>No content provided</p>
        </slot>
      </div>
      
      <!-- Footer (optional) -->
      <div class="modal-footer" v-if="$slots.footer">
        <slot name="footer"></slot>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue';

const emit = defineEmits(['close']);

const handleOverlayClick = () => {
  if (props.closeOnOverlayClick) {
    emit('close');
  }
};

// Access props for use in the function
const props = defineProps({
  title: {
    type: String,
    required: true
  },
  closeOnOverlayClick: {
    type: Boolean,
    default: true
  }
});
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 10000;
  padding: 1rem;
}

.modal-container {
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: .75rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.modal-title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 700;
  color: #1a202c;
}

.modal-close-btn {
  background: none;
  border: none;
  font-size: 2rem;
  line-height: 1;
  cursor: pointer;
  color: #666;
  transition: color 0.2s ease;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
}

.modal-close-btn:hover {
  color: #000;
  background: rgba(0, 0, 0, 0.05);
}

.modal-body {
  padding: .5rem 1rem;
  overflow-y: auto;
  flex: 1;
}

.modal-footer {
  padding: .5rem .75rem;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 0.75rem;
}
</style>
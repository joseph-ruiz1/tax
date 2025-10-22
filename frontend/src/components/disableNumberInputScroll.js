// Utility to disable mouse wheel and arrow key interactions with number inputs
export const disableNumberInputScroll = () => {
  // Function to handle mouse wheel events
  const handleWheel = (e) => {
    if (e.target.type === 'number') {
      e.target.blur()
    }
  }

  // Function to handle keyboard events
  const handleKeyDown = (e) => {
    if (e.target.type === 'number') {
      const key = e.charCode || e.keyCode
      // Disable Up (38) and Down (40) arrow keys
      if (key === 38 || key === 40) {
        e.preventDefault()
      }
    }
  }

  // Add event listeners to document
  document.addEventListener('wheel', handleWheel, { passive: false })
  document.addEventListener('keydown', handleKeyDown)

  // Return cleanup function
  return () => {
    document.removeEventListener('wheel', handleWheel)
    document.removeEventListener('keydown', handleKeyDown)
  }
}

// Alternative hook-based approach for React components
export const useDisableNumberInputScroll = () => {
  React.useEffect(() => {
    const cleanup = disableNumberInputScroll()
    return cleanup
  }, [])
}
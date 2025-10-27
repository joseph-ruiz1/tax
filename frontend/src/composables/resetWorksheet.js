export const resetWorksheet = (obj) => 
  Object.fromEntries(Object.keys(obj).map(key => [key, 0]))
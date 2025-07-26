/**
 * Utilidades para optimización de rendimiento
 */

// Debounce function para optimizar llamadas frecuentes
export const debounce = (func, wait) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

// Throttle function para limitar la frecuencia de ejecución
export const throttle = (func, limit) => {
  let inThrottle;
  return function() {
    const args = arguments;
    const context = this;
    if (!inThrottle) {
      func.apply(context, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
};

// Memoización simple para funciones costosas
export const memoize = (fn) => {
  const cache = new Map();
  return (...args) => {
    const key = JSON.stringify(args);
    if (cache.has(key)) {
      return cache.get(key);
    }
    const result = fn.apply(this, args);
    cache.set(key, result);
    return result;
  };
};

// Lazy loading para componentes
export const lazyLoad = (importFunc) => {
  return React.lazy(importFunc);
};

// Intersection Observer para lazy loading de imágenes
export const createIntersectionObserver = (callback, options = {}) => {
  return new IntersectionObserver(callback, {
    root: null,
    rootMargin: '0px',
    threshold: 0.1,
    ...options
  });
};

// Optimización de listas virtuales
export const virtualizeList = (items, itemHeight, containerHeight) => {
  const visibleCount = Math.ceil(containerHeight / itemHeight);
  const startIndex = Math.floor(window.scrollY / itemHeight);
  const endIndex = Math.min(startIndex + visibleCount, items.length);
  
  return {
    visibleItems: items.slice(startIndex, endIndex),
    startIndex,
    endIndex,
    totalHeight: items.length * itemHeight,
    offsetY: startIndex * itemHeight
  };
};

// Medición de rendimiento
export const measurePerformance = (name, fn) => {
  const start = performance.now();
  const result = fn();
  const end = performance.now();
  
  if (process.env.NODE_ENV === 'development') {
    console.log(`${name} took ${end - start} milliseconds`);
  }
  
  return result;
};

// Limpieza de memoria
export const cleanupMemory = () => {
  if (window.gc) {
    window.gc();
  }
};

// Optimización de imágenes
export const optimizeImage = (src, width, quality = 80) => {
  // Implementar optimización de imágenes según el dispositivo
  const isRetina = window.devicePixelRatio > 1;
  const actualWidth = isRetina ? width * 2 : width;
  
  return `${src}?w=${actualWidth}&q=${quality}`;
};

// Preload de recursos críticos
export const preloadResource = (href, as = 'fetch') => {
  const link = document.createElement('link');
  link.rel = 'preload';
  link.href = href;
  link.as = as;
  document.head.appendChild(link);
};

// Optimización de CSS crítico
export const loadCriticalCSS = () => {
  const criticalCSS = `
    /* CSS crítico para el primer render */
    .App { min-height: 100vh; }
    .loading { display: flex; justify-content: center; align-items: center; }
  `;
  
  const style = document.createElement('style');
  style.textContent = criticalCSS;
  document.head.appendChild(style);
};

// Optimización de fuentes
export const optimizeFonts = () => {
  // Preload de fuentes críticas
  preloadResource('/fonts/main-font.woff2', 'font');
  
  // Font display swap para mejor rendimiento
  const fontFace = `
    @font-face {
      font-family: 'MainFont';
      src: url('/fonts/main-font.woff2') format('woff2');
      font-display: swap;
    }
  `;
  
  const style = document.createElement('style');
  style.textContent = fontFace;
  document.head.appendChild(style);
};

// Optimización de bundle
export const codeSplitting = {
  // Lazy load de rutas
  routes: {
    dashboard: () => import('../components/StudentDashboard'),
    chat: () => import('../components/ChatPrincipal'),
    analysis: () => import('../components/AnalisisEmocional'),
    tutor: () => import('../components/PanelTutor')
  },
  
  // Lazy load de componentes pesados
  components: {
    charts: () => import('../components/Charts'),
    editor: () => import('../components/Editor'),
    calendar: () => import('../components/Calendar')
  }
};

// Optimización de estado
export const optimizeState = {
  // Normalización de estado para listas grandes
  normalizeList: (list, key = 'id') => {
    const entities = {};
    const ids = [];
    
    list.forEach(item => {
      entities[item[key]] = item;
      ids.push(item[key]);
    });
    
    return { entities, ids };
  },
  
  // Selector optimizado para Redux/Context
  createSelector: (selectors, combiner) => {
    let lastResult;
    let lastDependencies;
    
    return (state) => {
      const dependencies = selectors.map(selector => selector(state));
      
      if (lastDependencies && dependencies.every((dep, i) => dep === lastDependencies[i])) {
        return lastResult;
      }
      
      lastDependencies = dependencies;
      lastResult = combiner(...dependencies);
      return lastResult;
    };
  }
};

export default {
  debounce,
  throttle,
  memoize,
  lazyLoad,
  createIntersectionObserver,
  virtualizeList,
  measurePerformance,
  cleanupMemory,
  optimizeImage,
  preloadResource,
  loadCriticalCSS,
  optimizeFonts,
  codeSplitting,
  optimizeState
}; 
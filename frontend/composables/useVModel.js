import { computed } from 'vue'

export function useVModel(props, propName, emit) {
    return computed({
        get: () => props[propName],
        set: (val) => emit(`update:${propName}`, val),
    })
}
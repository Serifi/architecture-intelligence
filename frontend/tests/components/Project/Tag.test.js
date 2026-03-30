import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Tag from '../../../components/Project/Tag.vue'

describe('Project Tag Component', () => {
    it('does not render when tags array is empty', () => {
        const wrapper = mount(Tag, {
            props: { tags: [] }
        })
        expect(wrapper.find('div').exists()).toBe(false)
    })

    it('renders all tags in the array', () => {
        const tags = ['frontend', 'vue', 'testing']
        const wrapper = mount(Tag, {
            props: { tags }
        })
        const spanTags = wrapper.findAll('span')
        expect(spanTags).toHaveLength(3)
        expect(spanTags[0].text()).toBe('frontend')
        expect(spanTags[1].text()).toBe('vue')
        expect(spanTags[2].text()).toBe('testing')
    })
})

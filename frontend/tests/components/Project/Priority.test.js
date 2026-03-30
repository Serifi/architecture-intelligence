import { mount } from '@vue/test-utils'
import Priority from '../../../components/Project/Priority.vue'

describe('Priority.vue', () => {
    test('renders proper label based on priority prop', () => {
        const wrapper = mount(Priority, { props: { priority: 'high' } })
        expect(wrapper.text().toLowerCase()).toContain('high')
    })
})
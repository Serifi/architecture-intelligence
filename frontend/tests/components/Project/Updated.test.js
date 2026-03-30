import { mount } from '@vue/test-utils'
import Updated from '../../../components/Project/Updated.vue'

describe('Updated.vue', () => {
    test('renders "Updated" text or formatted date safely', () => {
        const wrapper = mount(Updated, { props: { date: '2025-11-08T12:00:00Z' } })
        const txt = wrapper.text()
        expect(txt.length).toBeGreaterThan(0)
        expect(txt.toLowerCase()).toMatch(/updated|2025|11|08/)
    })
})
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import List from '../../../components/Project/List.vue'

describe('Project List Component', () => {
    const mockProjects = [
        { projectID: 1, name: 'P1' },
        { projectID: 2, name: 'P2' }
    ]

    const globalStubs = {
        stubs: {
            Card: {
                props: ['project'],
                template: '<div class="card">{{ project.name }}</div>'
            },
            t: (k) => k
        },
        mocks: {
            $t: (k) => k
        }
    }

    it('renders a Card for each project', () => {
        const wrapper = mount(List, {
            props: { projects: mockProjects },
            global: globalStubs
        })
        expect(wrapper.findAll('.card')).toHaveLength(2)
    })

    it('renders empty state message when no projects', () => {
        const wrapper = mount(List, {
            props: { projects: [] },
            global: globalStubs
        })
        expect(wrapper.text()).toContain('projects.empty.title')
    })

    it('emits "add-click" when clicking the add button', async () => {
        const wrapper = mount(List, {
            props: { projects: [] },
            global: globalStubs
        })
        const addBtn = wrapper.find('.group.relative')
        await addBtn.trigger('click')
        expect(wrapper.emitted('add-click')).toBeTruthy()
    })
})

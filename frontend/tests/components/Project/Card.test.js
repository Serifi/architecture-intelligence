import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import Card from '../../../components/Project/Card.vue'

describe('Project Card Component', () => {
    const sampleProject = {
        projectID: 1,
        name: 'Test Project',
        description: 'Test Description',
        color: '#3498db',
        tags: ['ai', 'testing'],
        lastUpdated: new Date().toISOString()
    }

    const globalStubs = {
        stubs: {
            Header: { template: '<div class="header">{{ project.name }}</div>', props: ['project'] },
            Tag: { template: '<div class="tags">{{ tags.length }}</div>', props: ['tags'] },
            Updated: { template: '<div class="updated">Just now</div>', props: ['lastUpdated'] },
            Actions: { template: '<div class="actions"><button @click="$emit(\'edit\')">Edit</button></div>' }
        }
    }

    it('renders project name from header stub', () => {
        const wrapper = mount(Card, {
            props: { project: sampleProject },
            global: globalStubs
        })
        expect(wrapper.text()).toContain('Test Project')
    })

    it('shows actions when hovered', async () => {
        const wrapper = mount(Card, {
            props: { project: sampleProject },
            global: globalStubs
        })

        await wrapper.trigger('mouseenter')
        expect(wrapper.find('.actions').exists()).toBe(true)
    })

    it('emits "request-edit" when edit button is clicked', async () => {
        const wrapper = mount(Card, {
            props: { project: sampleProject },
            global: globalStubs
        })

        await wrapper.trigger('mouseenter') 
        await wrapper.find('.actions button').trigger('click')

        expect(wrapper.emitted('request-edit')).toBeTruthy()
        expect(wrapper.emitted('request-edit')[0][0]).toEqual(sampleProject)
    })

    it('sets border color based on project color on hover', async () => {
        const wrapper = mount(Card, {
            props: { project: sampleProject },
            global: globalStubs
        })

        await wrapper.trigger('mouseenter')
        const div = wrapper.find('div.relative')
        expect(div.attributes('style')).toContain('border-color: rgb(52, 152, 219)')
    })
})

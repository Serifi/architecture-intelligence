import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import Deletion from '../../../components/Project/Deletion.vue'

describe('Project Deletion Component', () => {
    const sampleProject = { projectID: 1, name: 'Project to Delete' }

    const globalStubs = {
        stubs: {
            Dialog: { template: '<div><slot /><slot name="footer" /></div>' },
            Button: {
                props: ['label', 'severity'],
                template: '<button :class="severity" @click="$emit(\'click\')">{{ label }}</button>'
            }
        }
    }

    it('renders project name in confirmation message', () => {
        const wrapper = mount(Deletion, {
            props: { visible: true, project: sampleProject },
            global: globalStubs
        })
        expect(wrapper.text()).toContain('Project to Delete')
    })

    it('emits "confirm" when delete button is clicked', async () => {
        const wrapper = mount(Deletion, {
            props: { visible: true, project: sampleProject },
            global: globalStubs
        })

        const deleteBtn = wrapper.find('button.danger')
        await deleteBtn.trigger('click')

        expect(wrapper.emitted('confirm')).toBeTruthy()
    })

    it('closes dialog when cancel button is clicked', async () => {
        const wrapper = mount(Deletion, {
            props: { visible: true, project: sampleProject },
            global: globalStubs
        })

        const cancelBtn = wrapper.find('button.secondary')
        await cancelBtn.trigger('click')

        expect(wrapper.emitted('update:visible')).toBeTruthy()
        expect(wrapper.emitted('update:visible')[0][0]).toBe(false)
    })
})

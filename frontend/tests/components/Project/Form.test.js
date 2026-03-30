import { mount } from '@vue/test-utils'
import Form from '../../../components/Project/Form.vue'

import { createPinia, setActivePinia } from 'pinia'

describe('Project Form', () => {
    beforeEach(() => {
        setActivePinia(createPinia())
    })

    const global = {
        stubs: {
            Dialog: { template: '<div><slot /><slot name="footer" /></div>' },
            Message: { template: '<div><slot /></div>' },
            InputText: {
                props: ['modelValue'],
                emits: ['update:modelValue'],
                template: `<input data-test="input-text" :value="modelValue" @input="$emit('update:modelValue', $event.target.value)" />`,
            },
            Textarea: {
                props: ['modelValue'],
                emits: ['update:modelValue'],
                template: `<textarea :value="modelValue" @input="$emit('update:modelValue', $event.target.value)" />`,
            },
            Select: {
                props: ['modelValue', 'options'],
                emits: ['update:modelValue'],
                template: `<select :value="modelValue" @change="$emit('update:modelValue', $event.target.value)">
                  <option v-for="opt in options" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
                </select>`,
            },
            ColorPicker: {
                props: ['modelValue'],
                emits: ['update:modelValue'],
                template: `<input type="color" :value="modelValue" @input="$emit('update:modelValue', $event.target.value)" />`,
            },
            Button: {
                props: ['label', 'disabled'],
                emits: ['click'],
                template: `<button :disabled="disabled" @click="$emit('click')">{{ label }}</button>`,
            },
        },
    }

    test('Create mode: emits "create" with default folder icon', async () => {
        const wrapper = mount(Form, { props: { visible: false }, global })

        await wrapper.setProps({ visible: true })
        await wrapper.vm.$nextTick()

        const input = wrapper.find('[data-test="input-text"]')
        await input.setValue('New Project')
        await wrapper.vm.$nextTick()

        const buttons = wrapper.findAll('button')
        const createBtn = buttons.at(buttons.length - 1)
        await createBtn.trigger('click')
        await wrapper.vm.$nextTick()

        const emitted = wrapper.emitted('create')
        expect(emitted).toBeTruthy()
        const payload = emitted[0][0]

        expect(payload.name).toBe('New Project')
        expect(payload.icon).toBe('folder')
        expect(payload.priority).toBe('medium')
        expect(payload.color).toMatch(/^#/)
    })

    test('Edit mode: fills fields and emits "save"', async () => {
        const project = {
            projectID: 1,
            name: 'Existing Project',
            description: 'Description',
            priority: 'high',
            icon: 'chart-line',
            color: '#ff0000',
            tags: ['tag1', 'tag2'],
        }

        const wrapper = mount(Form, { props: { visible: false, project }, global })

        await wrapper.setProps({ visible: true })
        await wrapper.vm.$nextTick()

        expect(wrapper.vm.form.name).toBe('Existing Project')

        const buttons = wrapper.findAll('button')
        const saveBtn = buttons.at(buttons.length - 1)
        await saveBtn.trigger('click')
        await wrapper.vm.$nextTick()

        const emitted = wrapper.emitted('save')
        expect(emitted).toBeTruthy()
        const { id, data } = emitted[0][0]

        expect(id).toBe(1)
        expect(data.name).toBe('Existing Project')
        expect(data.icon).toBe('chart-line')
    })
})
import { React } from 'jimu-core'
import _Widget from '../src/runtime/widget'
import { widgetRender, wrapWidget } from 'jimu-for-test'

const render = widgetRender()
describe('test providers widget', () => {
  it('should render providers widget with title', async () => {
    const Widget = wrapWidget(_Widget, {
      config: { title: 'Config with Ag data providers' }
    })
    const { findByTestId } = render(<Widget widgetId="Widget_1" />)

    const providersTitle = await findByTestId('providers-title')
    expect(providersTitle.textContent).toBe('Config with Ag data providers')
  })
})

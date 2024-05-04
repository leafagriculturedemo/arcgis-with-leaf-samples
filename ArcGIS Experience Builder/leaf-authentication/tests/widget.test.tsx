import { React } from 'jimu-core'
import _Widget from '../src/runtime/widget'
import { widgetRender, wrapWidget } from 'jimu-for-test'

const render = widgetRender()
describe('test authentication widget', () => {
  it('should render authentication widget with title', async () => {
    const Widget = wrapWidget(_Widget, {
      config: { title: 'Config with Ag data providers' }
    })
    const { findByTestId } = render(<Widget widgetId="Widget_1" />)

    const widgetTitle = await findByTestId('widget-title')
    expect(widgetTitle.textContent).toBe('Config with Ag data providers')
  })
})

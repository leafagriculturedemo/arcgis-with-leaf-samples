import { React } from 'jimu-core'
import _Widget from '../src/runtime/widget'
import { widgetRender, wrapWidget } from 'jimu-for-test'

const render = widgetRender()
describe('test file upload widget', () => {
  it('should render file upload widget with title', async () => {
    const Widget = wrapWidget(_Widget, {
      config: { title: 'Config with Ag data providers' }
    })
    const { findByTestId } = render(<Widget widgetId="Widget_1" />)

    const fileUploadTitle = await findByTestId('file-upload-title')
    expect(fileUploadTitle.textContent).toBe('Config with Ag data providers')
  })
})

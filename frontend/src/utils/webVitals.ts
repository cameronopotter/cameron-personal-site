import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals'

type ReportHandler = (metric: any) => void

const reportWebVitals = (onPerfEntry?: ReportHandler) => {
  if (onPerfEntry && onPerfEntry instanceof Function) {
    getCLS(onPerfEntry)
    getFID(onPerfEntry)
    getFCP(onPerfEntry)
    getLCP(onPerfEntry)
    getTTFB(onPerfEntry)
  }
}

export { getCLS, getFID, getFCP, getLCP, getTTFB }
export default reportWebVitals
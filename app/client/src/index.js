import React from 'react'
import ReactDOM from 'react-dom/client'
import '@fontsource/inter'
import './index.css'
import 'typeface-roboto'
import App from './App'
import { isFirefox } from './common/utils'

if (isFirefox) document.documentElement.classList.add('firefox')

const root = ReactDOM.createRoot(document.getElementById('root'))
root.render(<App />)

import React, { useState } from 'react'
import PropTypes from 'prop-types'
import AgregatorSelect from '../utils/agregator'

const MinimiseImpactOperation = (props) => {
  const access_token = useState(localStorage.getItem('access_token'))[0]
  const { requirement_file_id, manager, set_operation_result } = props
  const [_max_level, set_max_level] = useState('')
  const [limit, set_limit] = useState('')
  const [agregator, set_agregator] = useState('mean')

  const [max_level_error, set_max_level_error] = useState('')
  const [limit_error, set_limit_error] = useState('')

  const on_button_minimise_operation = () => {
    set_max_level_error('')
    set_limit_error('')

    if (_max_level < 1 && _max_level != -1) {
      set_max_level_error('The max level must be greater than 0 or equal -1')
      return
    }

    if (limit < 1) {
      set_limit_error('The limit must be greater than 0')
      return
    }

    const max_level = _max_level != -1 ? _max_level * 2 : _max_level
    const node_type = manager + "Package"

    fetch('http://localhost:8000/operation/file/minimize_impact', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${access_token}`
      },
      body: JSON.stringify({ requirement_file_id, limit, max_level, node_type, agregator })
    })
      .then((r) => r.json())
      .then((r) => {
        if ('success' === r.message) {
          set_operation_result(r)
        } else if ('no_dependencies' === r.message) {
          window.alert("The requirement file don't have dependencies")
        }
      })
  }

  return (
    <div className='flex-col flex'>
      <p>Minimise Impact Operation</p>
      <input
        value={limit}
        type='number'
        min='0'
        max='10'
        placeholder='Enter the limit here'
        onKeyDown={(e) => {
          if (e.key === 'Enter') on_button_minimise_operation()
        }}
        onChange={(ev) => set_limit(ev.target.value)}
        className='w-64 shadow appearance-none border rounded w-full py-2 px-2 text-gray-700 mb-3 leading-tight focus:outline-none focus:shadow-outline'
      />
      <input
        value={_max_level}
        type='number'
        min='-1'
        placeholder='Enter the max level here'
        onKeyDown={(e) => {
          if (e.key === 'Enter') on_button_minimise_operation()
        }}
        onChange={(ev) => set_max_level(ev.target.value)}
        className='w-64 shadow appearance-none border rounded w-full py-2 px-2 text-gray-700 mb-3 leading-tight focus:outline-none focus:shadow-outline'
      />
      <label className='text-red-600'>{limit_error}</label>
      <label className='text-red-600'>{max_level_error}</label>
      <AgregatorSelect agregator={agregator} set_agregator={set_agregator} />
      <input
        className='bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded'
        type='button'
        onClick={on_button_minimise_operation}
        value={'Apply'}
      />
    </div>
  )
}

MinimiseImpactOperation.propTypes = {
  requirement_file_id: PropTypes.string,
  manager: PropTypes.string,
  set_operation_result: PropTypes.func
}

export default MinimiseImpactOperation

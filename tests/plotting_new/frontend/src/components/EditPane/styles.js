export const overlayStyle = {
  position: 'fixed',
  top: 0,
  width: '500px',
  height: '100vh',
  backgroundColor: 'var(--sidebar-bg)',
  borderRight: '1px solid var(--border-color)',
  zIndex: 2000,
  transition: 'left 0.3s ease-in-out',
  display: 'flex',
  flexDirection: 'column',
  overflow: 'hidden'
};

export const headerStyle = {
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  padding: '20px',
  borderBottom: '1px solid var(--border-color)',
  backgroundColor: 'var(--card-background-color)'
};

export const contentStyle = {
  flex: 1,
  overflow: 'auto',
  padding: '20px'
};

export const sectionStyle = {
  marginBottom: '20px',
  backgroundColor: 'var(--card-background-color)',
  borderRadius: '8px',
  border: '1px solid var(--border-color)'
};

export const sectionHeaderStyle = {
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  padding: '16px',
  cursor: 'pointer',
  userSelect: 'none',
  transition: 'background-color 0.2s'
};

export const sectionContentStyle = {
  padding: '0 16px 16px',
  display: 'flex',
  flexDirection: 'column',
  gap: '12px',
  borderRadius: '0 0 8px 8px'
};

export const subsectionStyle = {
  padding: '10px',
  backgroundColor: 'var(--background-color)',
  borderRadius: '6px',
  border: '1px solid var(--border-color)'
};

export const subsectionHeaderStyle = {
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  marginBottom: '8px',
  cursor: 'pointer',
  userSelect: 'none'
};

export const subsectionTitleStyle = {
  fontSize: '0.9rem',
  fontWeight: '600',
  color: 'var(--text-color)'
};

export const chevronStyle = (expanded) => ({
  transform: expanded ? 'rotate(90deg)' : 'rotate(0deg)',
  transition: 'transform 0.2s',
  fontSize: '2rem',
  color: 'var(--text-color)',
  display: 'flex',
  alignItems: 'center'
});

export const inputGroupStyle = {
  display: 'flex',
  flexDirection: 'column',
  gap: '8px'
};

export const labelStyle = {
  fontSize: '0.85rem',
  fontWeight: 'normal',
  color: 'var(--text-color)'
};

export const inputStyle = {
  padding: '8px 12px',
  border: '1px solid var(--border-color)',
  borderRadius: '4px',
  backgroundColor: 'var(--background-color)',
  color: 'var(--text-color)',
  fontSize: '0.85rem',
  outline: 'none',
  transition: 'border-color 0.2s',
  colorScheme: 'inherit'
};

export const checkboxGroupStyle = {
  display: 'flex',
  alignItems: 'center',
  gap: '8px'
};

export const selectStyle = {
  padding: '8px 12px',
  border: '1px solid var(--border-color)',
  borderRadius: '4px',
  backgroundColor: 'var(--background-color)',
  color: 'var(--text-color)',
  fontSize: '0.85rem',
  outline: 'none',
  transition: 'border-color 0.2s',
  cursor: 'pointer',
  width: '100%'
};

export const legendItemStyle = {
  display: 'flex',
  alignItems: 'center',
  gap: '8px',
  padding: '4px 0'
};

export const legendItemInputStyle = {
  ...inputStyle,
  flex: 1,
  padding: '6px 10px'
};

export const backdropStyle = {
  position: 'fixed',
  top: 0,
  left: 0,
  right: 0,
  bottom: 0,
  backgroundColor: 'rgba(0, 0, 0, 0.3)',
  zIndex: 1999
};

export const closeButtonStyle = {
  background: 'none',
  border: 'none',
  fontSize: '1.5rem',
  cursor: 'pointer',
  color: 'var(--text-color)',
  padding: '4px',
  lineHeight: 1
};

export const fieldContainerStyle = {
  marginBottom: '12px'
};

export const checkboxStyle = {
  marginRight: '8px',
  cursor: 'pointer'
};

export const sliderStyle = {
  flex: 1,
  cursor: 'pointer',
  height: '4px'
};

export const colorInputStyle = {
  width: '30px',
  height: '30px',
  border: '1px solid var(--border-color)',
  borderRadius: '4px',
  cursor: 'pointer',
  padding: '0px',
  backgroundColor: 'var(--background-color)'
};

export const toggleButtonStyle = (isActive, disabled = false) => ({
  width: '30px',
  height: '30px',
  border: '1px solid var(--border-color)',
  borderRadius: '4px',
  backgroundColor: isActive ? 'var(--primary-color)' : 'var(--background-color)',
  color: isActive ? 'white' : 'var(--text-color)',
  fontSize: '14px',
  fontWeight: 'bold',
  cursor: disabled ? 'not-allowed' : 'pointer',
  opacity: disabled ? 0.5 : 1,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  transition: 'all 0.2s ease',
  userSelect: 'none'
});

// Data subsection specific styles
export const dataContainerStyle = {
  display: 'flex',
  flexDirection: 'column',
  gap: '12px',
  marginTop: '8px'
};

export const rowStyle = {
  display: 'grid',
  gridTemplateColumns: '80px 1fr',
  gap: '12px',
  alignItems: 'center'
};

export const traceOptionsContainerStyle = {
  backgroundColor: '#ECEEF0',
  border: '1px solid var(--border-color)',
  borderRadius: '6px',
  padding: '12px',
  display: 'flex',
  flexDirection: 'column',
  gap: '12px',
  boxShadow: 'inset 0 1px 3px rgba(0, 0, 0, 0.05)'
};

export const traceSectionHeaderStyle = {
  fontSize: '11px',
  fontWeight: '600',
  textTransform: 'uppercase',
  color: 'var(--text-secondary)',
  marginBottom: '8px',
  marginTop: '16px',
  letterSpacing: '0.5px'
};

export const flexRowStyle = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  width: '100%',
  gap: '8px'
};

export const flexGroupStyle = {
  display: 'flex',
  alignItems: 'center',
  gap: '2px'
};

export const smallInputStyle = {
  ...inputStyle,
  width: '50px',
  backgroundColor: '#ECEEF0'
};

export const dropdownTriggerStyle = {
  ...inputStyle,
  width: '80px',
  cursor: 'pointer',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  padding: '2px 4px',
  backgroundColor: '#ECEEF0'
};

export const dropdownStyle = {
  position: 'absolute',
  top: '100%',
  left: 0,
  right: 0,
  backgroundColor: '#ECEEF0',
  border: '1px solid var(--border-color)',
  borderRadius: '3px',
  boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
  zIndex: 1000
};

export const dropdownItemStyle = {
  padding: '8px',
  cursor: 'pointer',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  transition: 'background-color 0.2s'
};
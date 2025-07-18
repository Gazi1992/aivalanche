export const overlayStyle = {
  position: 'fixed',
  top: 0,
  width: '400px',
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
  border: '1px solid var(--border-color)',
  overflow: 'hidden'
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
  gap: '16px'
};

export const subsectionStyle = {
  padding: '12px',
  backgroundColor: 'var(--background-color)',
  borderRadius: '6px',
  border: '1px solid var(--border-color)'
};

export const subsectionHeaderStyle = {
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  marginBottom: '12px',
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
  fontSize: '0.8rem',
  color: 'var(--text-color)'
});

export const inputGroupStyle = {
  display: 'flex',
  flexDirection: 'column',
  gap: '8px'
};

export const labelStyle = {
  fontSize: '0.85rem',
  fontWeight: '500',
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
  transition: 'border-color 0.2s'
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
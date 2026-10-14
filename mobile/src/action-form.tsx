import { useEffect, useState } from 'react';
import {
  KeyboardAvoidingView,
  Modal,
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from 'react-native';

import { ActionButton, Field, Surface } from './components';
import { colors, spacing } from './theme';

export type MobileFormField = {
  key: string;
  label: string;
  initialValue?: string;
  placeholder?: string;
  required?: boolean;
  keyboardType?: 'default' | 'email-address' | 'numeric' | 'decimal-pad';
  secureTextEntry?: boolean;
  options?: readonly string[];
};

export function ActionForm({
  visible,
  title,
  description,
  fields,
  submitLabel,
  busy,
  onClose,
  onSubmit,
}: {
  visible: boolean;
  title: string;
  description?: string;
  fields: MobileFormField[];
  submitLabel: string;
  busy: boolean;
  onClose: () => void;
  onSubmit: (values: Record<string, string>) => void;
}) {
  const [values, setValues] = useState<Record<string, string>>({});
  const [validationError, setValidationError] = useState('');

  useEffect(() => {
    if (visible) {
      setValues(
        Object.fromEntries(fields.map((field) => [field.key, field.initialValue ?? ''])),
      );
      setValidationError('');
    }
  }, [visible, title]);

  const submit = () => {
    const missing = fields.find(
      (field) => field.required && !(values[field.key] ?? '').trim(),
    );
    if (missing) {
      setValidationError(`Vui lòng nhập ${missing.label.toLocaleLowerCase('vi')}.`);
      return;
    }
    setValidationError('');
    onSubmit(values);
  };

  return (
    <Modal animationType="slide" onRequestClose={onClose} transparent visible={visible}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
        style={styles.overlay}
      >
        <Pressable accessibilityRole="button" onPress={onClose} style={styles.backdrop} />
        <Surface style={styles.sheet}>
          <View style={styles.handle} />
          <Text style={styles.title}>{title}</Text>
          {description ? <Text style={styles.description}>{description}</Text> : null}
          <ScrollView keyboardShouldPersistTaps="handled" style={styles.fields}>
            {fields.map((field) => (
              <View key={field.key}>
                {field.options ? (
                  <View style={styles.optionGroup}>
                    <Text style={styles.label}>{field.label}{field.required ? ' *' : ''}</Text>
                    <View style={styles.options}>
                      {field.options.map((option) => {
                        const selected = values[field.key] === option;
                        return (
                          <Pressable
                            accessibilityRole="radio"
                            accessibilityState={{ selected }}
                            key={option}
                            onPress={() => setValues((current) => ({ ...current, [field.key]: option }))}
                            style={[styles.option, selected && styles.selectedOption]}
                          >
                            <Text style={[styles.optionText, selected && styles.selectedOptionText]}>{option}</Text>
                          </Pressable>
                        );
                      })}
                    </View>
                  </View>
                ) : (
                  <Field
                    keyboardType={field.keyboardType}
                    label={`${field.label}${field.required ? ' *' : ''}`}
                    onChangeText={(value) => setValues((current) => ({ ...current, [field.key]: value }))}
                    placeholder={field.placeholder}
                    secureTextEntry={field.secureTextEntry}
                    value={values[field.key] ?? ''}
                  />
                )}
              </View>
            ))}
            {validationError ? <Text accessibilityRole="alert" style={styles.error}>{validationError}</Text> : null}
          </ScrollView>
          <View style={styles.actions}>
            <ActionButton label="Hủy" onPress={onClose} secondary />
            <View style={styles.submit}><ActionButton busy={busy} label={submitLabel} onPress={submit} /></View>
          </View>
        </Surface>
      </KeyboardAvoidingView>
    </Modal>
  );
}

const styles = StyleSheet.create({
  overlay: { flex: 1, justifyContent: 'flex-end' },
  backdrop: { ...StyleSheet.absoluteFill, backgroundColor: '#10271D99' },
  sheet: { borderBottomLeftRadius: 0, borderBottomRightRadius: 0, maxHeight: '90%', padding: spacing.lg },
  handle: { alignSelf: 'center', backgroundColor: colors.line, borderRadius: 3, height: 5, marginBottom: spacing.md, width: 42 },
  title: { color: colors.ink, fontSize: 19, fontWeight: '900' },
  description: { color: colors.muted, fontSize: 12, lineHeight: 18, marginTop: spacing.xs },
  fields: { marginTop: spacing.md },
  optionGroup: { marginBottom: spacing.md },
  label: { color: colors.ink, fontSize: 13, fontWeight: '700', marginBottom: spacing.xs },
  options: { flexDirection: 'row', flexWrap: 'wrap', gap: spacing.xs },
  option: { backgroundColor: colors.paper, borderColor: colors.line, borderRadius: 16, borderWidth: 1, paddingHorizontal: 12, paddingVertical: 9 },
  selectedOption: { backgroundColor: colors.forest, borderColor: colors.forest },
  optionText: { color: colors.muted, fontSize: 12, fontWeight: '700' },
  selectedOptionText: { color: colors.white },
  error: { color: colors.red, fontSize: 12, marginBottom: spacing.sm },
  actions: { flexDirection: 'row', gap: spacing.sm, paddingTop: spacing.sm },
  submit: { flex: 1 },
});

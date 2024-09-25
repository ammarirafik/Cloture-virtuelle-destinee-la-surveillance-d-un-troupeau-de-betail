
// Import des composants nécessaires
import React, { useEffect, useState } from 'react';
import { StatusBar } from 'expo-status-bar';
import { StyleSheet, View } from 'react-native';
import { initializeApp } from 'firebase/app';
import { getDatabase, ref, onValue } from 'firebase/database';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import Screen1 from './src/screen1';
import Screen2 from './src/screen2';
import Screen3 from './src/screen3';
import Screen4 from './src/screen4';
import { AppRegistry } from 'react-native'; // Import pour l'enregistrement de l'application
import { name as appName } from './app.json'; // Import du nom de l'application depuis app.json

// Configuration Firebase
const firebaseConfig = {
  apiKey: "AIzaSyCzjHj6sLqskwGweN5aP0XxuRsWVGlM1BM",
  authDomain: "mouton-67334.firebaseapp.com",
  projectId: "mouton-67334",
  storageBucket: "mouton-67334.appspot.com",
  messagingSenderId: "1033808874086",
  appId: "1:1033808874086:android:d2396b253d8f94c4f77ba7",
  databaseURL: "https://mouton-67334-default-rtdb.firebaseio.com",
  // measurementId: "G-5KN15EML5B"
};

// Initialisation de Firebase
const app = initializeApp(firebaseConfig);

// Création de la pile de navigation
const Stack = createStackNavigator();

// Composant principal de l'application
export default function App() {
  const [mouton, setMouton] = useState(null);

  // Effet pour récupérer les données depuis Firebase
  useEffect(() => {
    const database = getDatabase(app);
    const moutonRef = ref(database, 'moutons');

    const unsubscribe = onValue(moutonRef, (snapshot) => {
      const moutonValue = snapshot.val();
      if (moutonValue) {
        setMouton(moutonValue);
      } else {
        console.log('Aucun mouton disponible dans Firebase');
      }
    });

    // Nettoyage lors du démontage du composant
    return () => unsubscribe();
  }, []);

  // Retourne l'interface de navigation
  return (
    <NavigationContainer>
      <View style={styles.container}>
        <Stack.Navigator initialRouteName="Screen1">
          <Stack.Screen name="Screen1" component={Screen1} />
          <Stack.Screen name="Screen2" component={Screen2} />
          <Stack.Screen name="Screen3">
            {(props) => <Screen3 {...props} mouton={mouton} />}
          </Stack.Screen>
          <Stack.Screen name="Screen4" component={Screen4} />
        </Stack.Navigator>
        <StatusBar style="auto" />
      </View>
    </NavigationContainer>
  );
}

// Styles
const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
});

// Enregistrement de l'application
AppRegistry.registerComponent(appName, () => App);
